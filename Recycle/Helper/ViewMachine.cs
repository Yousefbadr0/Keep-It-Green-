using Recycle.Data.Models;
using Recycle.Dtos;
namespace Recycle.Helper
{
    public class ViewMachine
    {
        public List<GetMachine> view (List< Machine> machines)
        {
           var machineDtos = new List<GetMachine>();
            foreach (var machine in machines)
            {
                machineDtos.Add(new GetMachine
                {
                    Id = machine.Id,
                    Name = machine.Name,
                    Location = machine.Location,
                    IsAvailable = machine.IsAvailable
                });
            }
            return machineDtos;
        }
    }
}
