using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Recycle.Dtos;
using Recycle.Services;

namespace Recycle.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class PromoController : ControllerBase
    {
        private readonly RewardServices _rewards;
        public PromoController(RewardServices rewards)
        {
            _rewards = rewards;
        }

        [Authorize(Roles = "Admin")]
        [HttpPost]
        public IActionResult AddPromo(AddPromoCode promo)
        {
            try
            {
                _rewards.AddPromo(promo);
                return Created();
            }
            catch (Exception ex)
            {
                return BadRequest(new { Message = ex.Message });
            }
        }

        // Any authenticated user can browse the promo codes they could redeem.
        [HttpGet]
        public IActionResult GetAvailable() => Ok(_rewards.GetAvailablePromos());
    }
}
