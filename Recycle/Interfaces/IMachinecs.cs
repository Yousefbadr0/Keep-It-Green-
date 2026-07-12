
using Recycle.Data.Models;
using Recycle.Dtos;

namespace Recycle.Interfaces
{
    public interface IMachinecs
    {
        IQueryable<Machine> GetAllMachines();
       
        

        void AddMachine(AddMachine machine);
    
           void UpdateMachine(int id, UpdateStatusMachine machine);

        void DeleteMachine(int id);

    }
}
