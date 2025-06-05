cmake_minimum_required(VERSION 3.16)
project(MuonLArSim)

find_package(Geant4 REQUIRED)

add_executable(MuonLArSim
    main.cc
    DetectorConstruction.cc
    PrimaryGeneratorAction.cc
    MySensitiveDetector.cc
    MyPhysicsList.cc
)

target_include_directories(MuonLArSim PRIVATE ${Geant4_INCLUDE_DIRS})
target_link_libraries(MuonLArSim ${Geant4_LIBRARIES})
