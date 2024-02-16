#include <fstream>
#include <iostream>
#include <json/json.h>
class MaltReaderJSON {
public:
  MaltReaderJSON(const char *fname) {
    std::ifstream ifs;
    ifs.open(fname);
    
    Json::CharReaderBuilder builder;
    builder["collectComments"] = true;
    JSONCPP_STRING errs;
    
    if (!parseFromStream(builder, ifs, &data_, &errs)) {
      std::cout << errs << std::endl;
    }
  }
  void print() {
    for (auto const& id : data_.getMemberNames()) {
      std::cout << id << std::endl;
    }
    auto& config = data_["config"]["time"];
    std::cout << std::endl << "time:" << std::endl;
    for (auto const& id : config.getMemberNames()) {
      std::cout << id << ":" << config[id] << std::endl;
    }
  }
private:
  Json::Value data_;
};
