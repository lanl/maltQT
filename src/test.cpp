#include "maltReaderJSON.hpp"
int main(int argc, char* argv[]) {
  auto jr = new MaltReaderJSON(argv[1]);
  jr->print();
  return 0;
}

