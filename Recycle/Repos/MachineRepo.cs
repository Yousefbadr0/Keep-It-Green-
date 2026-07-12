using Recycle.Interfaces;
using Recycle.Dtos;
using Recycle.Data;
using Recycle.Data.Models;
using Microsoft.EntityFrameworkCore;

namespace Recycle.Repos
{
    public class MachineRepo: IMachinecs
    {
        private readonly Context _context;
        public MachineRepo(Context context)
        {
            _context = context;
        }
        public IQueryable<Machine> GetAllMachines()
        {
            return _context.Machines.AsQueryable();
        }
       
       

        public void AddMachine(AddMachine machine)
        {
            var newMachine = new Machine
            {
                Name = machine.Name,
                Location = machine.Location,
                IsAvailable = true
            };
            _context.Machines.Add(newMachine);
            _context.SaveChanges();
        }

        public void UpdateMachine(int id, UpdateStatusMachine machine)
        {
            var existingMachine = _context.Machines.Find(id);
            if (existingMachine != null)
            {
                existingMachine.IsAvailable = machine.IsAvailable;
                _context.SaveChanges();
            }
        }

        public void DeleteMachine(int id)
        {
            var existingMachine = _context.Machines.Find(id);
            if (existingMachine != null)
            {
                _context.Machines.Remove(existingMachine);
                _context.SaveChanges();
            }
        }
    }
}
