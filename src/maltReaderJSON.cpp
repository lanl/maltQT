#include <cstdint>
#include <regex>
#include <sstream>

#include "json/json.h"
#include "maltReaderJSON.hpp"

MaltReaderJSON::MaltReaderJSON(const char *fname) : fname_(fname) {
  std::ifstream ifs;
  ifs.open(fname);

  Json::CharReaderBuilder builder;
  builder["collectComments"] = true;
  JSONCPP_STRING errs;

  if (!parseFromStream(builder, ifs, &data_, &errs)) {
    std::cout << errs << std::endl;
  }

  data_["sites"]["strings"];
  instr_ = data_["sites"]["instr"];
  auto &jNames = data_["sites"]["strings"];
  const int nSize = jNames.size();

  std::vector<std::string> names;
  names.reserve(nSize);
  for (auto &s : jNames) {
    names.push_back(s.asString());
  }

  for (auto const &item : instr_.getMemberNames()) {
    auto &iDict = instr_[item];
    std::string idFile("");
    if (iDict.isMember("file")) {
      idFile = names[iDict["file"].asInt()];
    }
    auto idFunction = names[iDict["function"].asInt()];
    int lineNo = (iDict.isMember("line") ? iDict["line"].asInt() : -1);
    instrMap_[item] = {.function = idFunction, .file = idFile, .line = lineNo};
    nameMap_[idFunction].push_back(item);
  }
  // Set up rapid lookup index
  index_();
}

void MaltReaderJSON::addToIndex_(std::string name, int count, size_t inclusive,
				 size_t exclusive, size_t globalPeak){
  //< Utility routint that enables indexed searching for higher speed
  if (count_.find( name ) == count_.end()) {
    count_[name] = 0;
    inclusive_[name] = exclusive_[name] = 0;
  }
  count_[name] += count;
  inclusive_[name] += inclusive;
  exclusive_[name] += exclusive;

  if (globalPeak > 0) { 
    if (globalPeak_.find( name ) == globalPeak_.end()) {
      globalPeak_[name] = std::array<size_t,2>{0,0};
    }
    globalPeak_[name][0] += globalPeak;
    if (exclusive > 0) {
      globalPeak_[name][1] += globalPeak;
    }
  }
}

void MaltReaderJSON::index_() {
  // Enables indexing for searches by creating a reverse lookup.
  // This populates self.inclusive, self.exclusive and
  // self.globalPeaks all of which are dictionaries with the name
  // of a subroutine as key and the appropriate memory as value,
  // except for self.globalPeak which is a list with
  // [inclusiveGlobalPeak, exclusiveGlobalPeak] as values
  const std::vector<std::string> ignores({"calloc", "malloc", "posix_memalign",
                    "realloc", "operator new(unsigned long)" });

  auto &stats = data_["stacks"]["stats"];
  for (Json::Value::ArrayIndex i = 0; i != stats.size(); i++) {
    auto &item = stats[i];
    auto &infos = item["infos"];
    int count = infos["alloc"]["count"].asInt();
    size_t glop, inclusive, exclusive;
    std::stringstream(infos["alloc"]["sum"].asString()) >> inclusive;
    std::stringstream(infos["globalPeak"].asString()) >> glop;
    exclusive = inclusive;
    if (inclusive == 0  and glop == 0) {
      continue;
    }
    auto &theStack = item["stack"];
    auto &theStackId = item["stackId"];
    for (Json::Value::ArrayIndex j = 0; j != theStack.size(); j++) {
      auto entry = theStack[j].asString();
      bool a = false;
      for (auto & ignore : ignores) {
	if (ignore.compare(entry) == 0) {
	  a = true;
	  break;
	}
      }
      if (a ||
	  (entry.rfind("__gnu_cxx::",0) == 0) ||
	  (entry.find("/libstdc++/") != entry.npos)) {
	continue;
      }
      callsite_[theStackId.asString()].push_back(entry);
      auto &name = instrMap_[entry].function;
      addToIndex_(name, count, inclusive, exclusive, glop);
      exclusive = 0;
    }
    if (exclusive > 0) {
      // looks like an empty stack
      addToIndex_(theStackId.asString(), count, inclusive, exclusive, glop);
    }
  }
}

std::map<std::string,std::pair<size_t,int>>
MaltReaderJSON::allocsByName(const std::string name=std::string("."), bool exclusive=false) {
  std::map<std::string,std::pair<size_t,int>> retVal;
  //Given a name, prints all allocations associated by that name
  auto reFound = std::regex(name, std::regex_constants::icase);
  auto &base = (exclusive?exclusive_ : inclusive_);
  for(auto &entry: base) {
    if (std::regex_search(entry.first, reFound)) {
      retVal[entry.first] = std::make_pair(entry.second, count_[entry.first]);
    }
  }
  return retVal;
}

void MaltReaderJSON::print() {
  auto allocs = allocsByName("teos");
  for (auto const &entry : allocs) {
    std::cout << entry.first << ":" << entry.second.first << " count="<< entry.second.second << std::endl;
  }
  return;
  for (auto const &id : data_.getMemberNames()) {
    std::cout << id << std::endl;
  }
  auto &config = data_["config"]["time"];
  std::cout << std::endl << "time:" << std::endl;
  for (auto const &id : config.getMemberNames()) {
    std::cout << id << ":" << config[id] << std::endl;
  }
  for (auto const &[key, val] : instrMap_) {
    std::cout << key << ": function=" << val.function << ", file=" << val.file
              << ", line=" << val.line << std::endl;
  }
}
