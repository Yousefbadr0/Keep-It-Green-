using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Recycle.Dtos;
using Recycle.Services;
using System.Security.Claims;
namespace Recycle.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class OtpController : ControllerBase
    {
        private readonly OtpServices _otpServices;
        public OtpController(OtpServices otpServices)
        {
            _otpServices = otpServices;
        }
        [HttpGet("Generate/{MachineId}")]
        public IActionResult GenerateOtp(int MachineId)
        {
            var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (userId is null) return Unauthorized(new { Message = "User not authenticated" });

            var otp = _otpServices.CheckBeforGenerationOtp(userId,MachineId);

            if (otp != null)
            {
                return Ok(new { Otp = otp, Message = "OTP generated successfully. Valid for 5 minutes." });
            }
            else
            {
                return BadRequest(new { Message = "Try Again" });

            }
        }

        [HttpGet("Verify")]
        public IActionResult VerifyOtp(string otp)
        {
            var result = _otpServices.VerfiyOtp(otp);
            if (result != null)
            {
                return Ok(new { Message = "OTP verified successfully", OtpId = result.Id });
            }
            else
            {
                return BadRequest(new { Message = "Invalid or expired OTP" });
            }
        }

        // ATM-style pairing: the user scans the machine's QR (or types the code) to open the session.
        [Authorize(Roles = "User")]
        [HttpPost("Pair")]
        public IActionResult Pair([FromBody] PairRequest req)
        {
            var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
            try
            {
                var result = _otpServices.PairSession(req.Code, userId!);
                return Ok(new { Message = "Session paired", MachineId = result.MachineId });
            }
            catch (Exception ex)
            {
                return BadRequest(new { Message = ex.Message });
            }
        }

        // The user taps "Finish session" on the phone -> stop their active session so the
        // machine's status poll ends it and returns to the idle screen.
        [Authorize(Roles = "User")]
        [HttpPost("EndSession")]
        public IActionResult EndSession()
        {
            var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
            var count = _otpServices.EndUserSessions(userId!);
            return Ok(new { Message = "Session ended", Ended = count });
        }

        // The phone polls this while on the live-session screen so it auto-closes when the
        // machine ends the session (Finish / idle timeout) — no manual Finish tap needed.
        [Authorize(Roles = "User")]
        [HttpGet("session/active")]
        public IActionResult SessionActive()
        {
            var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
            return Ok(new { Active = _otpServices.UserHasActiveSession(userId!) });
        }
    }
}
