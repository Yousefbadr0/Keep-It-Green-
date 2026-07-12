using Recycle.Interfaces;
using Recycle.Dtos;
using Recycle.Helper;
using Microsoft.EntityFrameworkCore;
namespace Recycle.Services
{
    public class MachineServices
    {
        private readonly IMachinecs _machineRepo;
        private readonly ViewMachine _viewMachineHelper;
        public MachineServices(IMachinecs machineRepo, ViewMachine viewMachineHelper)
        {
            _machineRepo = machineRepo;
            _viewMachineHelper = viewMachineHelper;
        }

        public List<GetMachine> GetMachines()
        {
            var machines = _machineRepo.GetAllMachines().ToList();
            var result = _viewMachineHelper.view(machines);
            return result;
        }

        public List<GetMachine> GetMachinesBySearch(string city)
        {
            var machines = _machineRepo.GetAllMachines().Where(m => EF.Functions.Like(m.Location, $"%{city}%")).ToList();
            var result = _viewMachineHelper.view(machines);
            return result;
        }

        public void AddMachine(AddMachine machine)
        {

            _machineRepo.AddMachine(machine);


        }

        public void DeleteMachine(int id)
        {

            _machineRepo.DeleteMachine(id);
        }
        public void UpdateMachine(int id, UpdateStatusMachine machine)
        {
            _machineRepo.UpdateMachine(id, machine);
        }
    }
}
