#include "MyPhysicsList.hh"
#include "G4DecayPhysics.hh"
#include "G4EmStandardPhysics.hh"
#include "G4StepLimiter.hh"
#include "G4ProcessManager.hh"
#include "G4ParticleTable.hh"

MyPhysicsList::MyPhysicsList() {
    RegisterPhysics(new G4DecayPhysics());
    RegisterPhysics(new G4EmStandardPhysics());
}

void MyPhysicsList::ConstructParticle() {
    G4VModularPhysicsList::ConstructParticle();
}

void MyPhysicsList::ConstructProcess() {
    G4VModularPhysicsList::ConstructProcess();

    auto particleTable = G4ParticleTable::GetParticleTable();
    auto iter = particleTable->GetIterator();
    iter->reset();

    while ((*iter)()) {
        G4ParticleDefinition* particle = iter->value();
        G4ProcessManager* pmanager = particle->GetProcessManager();

        if (particle->GetPDGCharge() != 0.0 && !particle->IsShortLived() && pmanager) {
            pmanager->AddProcess(new G4StepLimiter(), -1, -1, 3);
        }
    }
}
