using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Recycle.Services;
using System.Security.Claims;

namespace Recycle.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize(Roles = "User")]
    public class RedemptionController : ControllerBase
    {
        private readonly RewardServices _rewards;
        public RedemptionController(RewardServices rewards)
        {
            _rewards = rewards;
        }

        // Redeem coins for a promo code.
        [HttpPost("{promoId}")]
        public IActionResult Redeem(int promoId)
        {
            var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (userId is null) return Unauthorized(new { Message = "User not authenticated" });
            try
            {
                var result = _rewards.Redeem(userId, promoId);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return BadRequest(new { Message = ex.Message });
            }
        }

        // The user's redemption history.
        [HttpGet("My")]
        public IActionResult MyRedemptions()
        {
            var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (userId is null) return Unauthorized(new { Message = "User not authenticated" });
            return Ok(_rewards.GetMyRedemptions(userId));
        }
    }
}
