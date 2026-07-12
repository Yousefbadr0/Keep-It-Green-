using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Recycle.Services;
using Recycle.Dtos;

namespace Recycle.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class MachineController : ControllerBase
    {
        private readonly MachineServices machineServices;
        public MachineController(MachineServices machineServices)
        {
            this.machineServices = machineServices;
        }
        
        [HttpGet]
        public async Task<IActionResult> GetMachines()
        {
            var machines = machineServices.GetMachines();
            return Ok(machines);
        }

        [HttpGet("Search")]
        public async Task<IActionResult> GetMachinesBySearch(string city)
        {
            var machines = machineServices.GetMachinesBySearch(city);
            return Ok(machines);
        }
        [Authorize (Roles = "Admin")]
        [HttpPost]
        public async Task<IActionResult> AddMachine(AddMachine machine)
        {
            machineServices.AddMachine(machine);
            return Created();
        }
        [Authorize(Roles = "Admin")]
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteMachine(int id)
        {
            machineServices.DeleteMachine(id);
            return NoContent();
        }
        [Authorize(Roles = "Admin")]
        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateMachine(int id, UpdateStatusMachine machine)
        {
            machineServices.UpdateMachine(id, machine);
            return NoContent();
        }
    }
}
