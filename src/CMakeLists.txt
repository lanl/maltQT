######################################
# CMakeLists.txt for MCNP QT interface
######################################
cmake_minimum_required(VERSION 3.7.0)

project(malt-qt2 LANGUAGES CXX)

# option(MQT2_TEST "Build test program" OFF)

# Specify default build
set(CMAKE_BUILD_TYPE Release CACHE STRING "Buld type")

# On windows export all symbols
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS 1)

# Specify sources
set(SOURCES
  test.cpp
  maltReaderJSON.cpp
  )
set(HEADERS
  maltReaderJSON.hpp
  maltVCore.hpp
  maltVTimeline.hpp
  maltVChart.hpp
  maltVStack.hpp
  )

add_executable(malt-qt2 ${SOURCES} ${HEADERS})

include_directories(${JSONCPP_DIR}/include)
target_link_directories(malt-qt2 PRIVATE ${JSONCPP_DIR}/lib)
target_link_libraries(malt-qt2 jsoncpp)
set_property(TARGET malt-qt2 PROPERTY CXX_STANDARD 17)

# Add Qt specific flags and libraries
set(CMAKE_AUTOMOC ON)
find_package(Qt6 COMPONENTS Widgets Charts Core Gui REQUIRED)
target_link_libraries(malt-qt2 Qt6::Widgets Qt6::Core Qt6::Gui Qt6::Charts)
set_target_properties(malt-qt2 PROPERTIES AUTOMOC ${CMAKE_AUTOMOC})

install(TARGETS malt-qt2)

