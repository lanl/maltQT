#include <QApplication>
//#include "maltReaderJSON.hpp"
#include "maltVCore.hpp"

int main(int argc, char* argv[]) {
  //  auto jr = new MaltReaderJSON(argv[1]);
  //jr->print();

  std::vector<MaltVCore*> qtm;
  auto app = QApplication(argc,argv);
  qtm.push_back(new MaltVCore(argv[1]));
  return app.exec();

  
  return 0;
}

