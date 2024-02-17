#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <string>

#include "json/json.h"
struct instrMapItem {
  std::string function;
  std::string file;
  int line;
};

//> Class for holding data from MALT JSON output
class MaltReaderJSON {
public:
  // Functions

  //> Returns the file name that populated this class
  std::string fname() { return fname_; }

  //> Constructor
  MaltReaderJSON(const char *fname);

  //> Debug printing of information, will be removed
  void print();

  Json::Value const &data() { return data_; }   //< access jsoncpp data
  Json::Value const &instr() { return instr_; } //< instr accessor
  std::map<std::string, struct instrMapItem> &instrMap() {
    return instrMap_;
  } //< instrMap accessor
  std::map<std::string, std::vector<std::string>> &nameMap() {
    return nameMap_;
  } //< nameMap accessor

private:
  std::string fname_; //< The file from which this class was populated
  Json::Value data_;  //< struct returned by jsoncpp on reading input file
  Json::Value instr_; //< The instructions dictionary within MALT
  std::map<std::string, struct instrMapItem>
      instrMap_; //< Lookup for converting instruction to file / function / line
  std::map<std::string, std::vector<std::string>>
      nameMap_; //< Reverse lookup from function to stacks
  std::map<std::string, int> count_;
  std::map<std::string, size_t> inclusive_;
  std::map<std::string, size_t> exclusive_;
  std::map<std::string, std::array<size_t,2>> globalPeak_;
  std::map<std::string, std::vector<std::string>> callsite_;

  //Methods
  void index_(); //< Indexes functions for easy reverse lookup
  void addToIndex_(std::string name, int count, size_t inclusive,
				   size_t exclusive, size_t globalPeak);
};
