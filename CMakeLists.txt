cmake_minimum_required(VERSION 3.16)
project(MuonLArSim)

find_package(Geant4 REQUIRED)

execute_process(
  COMMAND geant4-config --cxxstd
  OUTPUT_VARIABLE GEANT4_CXX_STD
  OUTPUT_STRIP_TRAILING_WHITESPACE
)

message(STATUS "Geant4 requires C++${GEANT4_CXX_STD}")

set(CMAKE_CXX_STANDARD ${GEANT4_CXX_STD})
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(MuonLArSim
    main.cc
    DetectorConstruction.cc
    PrimaryGeneratorAction.cc
    MySensitiveDetector.cc
    MyPhysicsList.cc
    MyRunAction.cc
)

target_include_directories(MuonLArSim PRIVATE ${Geant4_INCLUDE_DIRS})
target_link_libraries(MuonLArSim ${Geant4_LIBRARIES})
