#ifndef PHYSICS_LIST_HH
#define PHYSICS_LIST_HH

#include "G4VModularPhysicsList.hh"

class MyPhysicsList : public G4VModularPhysicsList {
public:
    MyPhysicsList();
    virtual ~MyPhysicsList() = default;

    void ConstructParticle() override;
    void ConstructProcess() override;
};

#endif
