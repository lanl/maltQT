
#include "maltReaderJSON.hpp"
#include <json/json.h>

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
}

void MaltReaderJSON::print() {
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
