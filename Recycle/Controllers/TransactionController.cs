using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Recycle.Services;
using Recycle.Dtos;
using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Recycle.Migrations;
namespace Recycle.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class TransactionController : ControllerBase
    {
        private readonly TransactionServices _transactionServices;
        public TransactionController(TransactionServices transactionServices)
        {
            _transactionServices = transactionServices;
        }
        [Authorize(Roles = "User")]
        [HttpGet("User")]
        public async Task<IActionResult> GetTransactionsByUserId()
        {
            var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (userId is null) return Unauthorized(new { Message = "User not authenticated" });
            var transactions = _transactionServices.GetTransactionByUserId(userId);
            return Ok(transactions);
        }
        [Authorize(Roles = "User")]
        [HttpPost]
        public async Task<IActionResult> AddTransaction(AddTransaction transaction)
        {
            try
            {
                _transactionServices.AddTransaction(transaction);
                return Created();

            }



            catch (Exception ex)
            {
                return BadRequest(new { Message = ex.Message });
            }

        }
        [Authorize(Roles = "Admin")]
        [HttpGet("Admin/{machineId}")]
        public async Task<IActionResult> GetViewTransactionForAdmins(
            int machineId, [FromQuery] int page = 1, [FromQuery] int pageSize = 200)
        {
            var transactions = _transactionServices.GetViewTransactionForAdmins(machineId, page, pageSize);
            return Ok(transactions);
        }

        [Authorize(Roles = "User")]
        [HttpGet("EndTransaction/{otpId}")]
        public async Task<IActionResult> EndTransaction(int otpId)
        {
            _transactionServices.EndTransaction(otpId);
            return Ok(new {Message="End Sucessfully"});
        }
    }
}
