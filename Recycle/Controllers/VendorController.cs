using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Recycle.Dtos;
using Recycle.Services;

namespace Recycle.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class VendorController : ControllerBase
    {
        private readonly RewardServices _rewards;
        public VendorController(RewardServices rewards)
        {
            _rewards = rewards;
        }

        [Authorize(Roles = "Admin")]
        [HttpPost]
        public IActionResult AddVendor(AddVendor vendor)
        {
            try
            {
                _rewards.AddVendor(vendor);
                return Created();
            }
            catch (Exception ex)
            {
                return BadRequest(new { Message = ex.Message });
            }
        }

        [HttpGet]
        public IActionResult GetVendors() => Ok(_rewards.GetVendors());
    }
}
