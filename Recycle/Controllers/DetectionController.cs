using Microsoft.AspNetCore.Mvc;
using Recycle.Dtos;
using Recycle.Services;

namespace Recycle.Controllers
{
    /// <summary>
    /// Endpoint for the recycling machine (YOLO laptop) to submit detections.
    /// Authenticated by the X-Machine-Key header instead of a user JWT, because the
    /// machine is not a logged-in user — the OTP in the body identifies the session.
    /// </summary>
    [Route("api/[controller]")]
    [ApiController]
    public class DetectionController : ControllerBase
    {
        private readonly TransactionServices _transactionServices;
        private readonly OtpServices _otpServices;
        private readonly MachineServices _machineServices;
        private readonly RewardServices _rewardServices;
        private readonly IConfiguration _configuration;

        public DetectionController(TransactionServices transactionServices, OtpServices otpServices,
            MachineServices machineServices, RewardServices rewardServices, IConfiguration configuration)
        {
            _transactionServices = transactionServices;
            _otpServices = otpServices;
            _machineServices = machineServices;
            _rewardServices = rewardServices;
            _configuration = configuration;
        }

        private bool KeyOk(string? machineKey)
        {
            var expectedKey = _configuration["Machine:ApiKey"];
            if (string.IsNullOrEmpty(expectedKey) || string.IsNullOrEmpty(machineKey))
                return false;
            // Constant-time comparison — a plain == leaks key length/prefix via timing.
            return System.Security.Cryptography.CryptographicOperations.FixedTimeEquals(
                System.Text.Encoding.UTF8.GetBytes(machineKey),
                System.Text.Encoding.UTF8.GetBytes(expectedKey));
        }

        // ── ATM-style flow ──────────────────────────────────────────────────────

        // 1) The kiosk starts a session -> gets a pairing code to show as QR + digits.
        [HttpPost("session/start")]
        public IActionResult StartSession(
            [FromHeader(Name = "X-Machine-Key")] string? machineKey,
            [FromQuery] int machineId)
        {
            if (!KeyOk(machineKey))
                return Unauthorized(new { Message = "Invalid or missing machine key." });

            var machine = _machineServices.GetMachines().FirstOrDefault(m => m.Id == machineId);
            if (machine == null)
                return NotFound(new { Message = $"Machine {machineId} does not exist." });

            var code = _otpServices.StartMachineSession(machineId);
            return Ok(new StartSessionResult
            {
                PairingCode = code,
                MachineId = machineId,
                MachineName = machine.Name,
                LocationName = machine.Location,
                ExpiresInSeconds = 900,
            });
        }

        // 2) The kiosk polls until a user pairs (scans the QR or types the code in the app).
        [HttpGet("session/{code}/status")]
        public IActionResult SessionStatus(
            [FromHeader(Name = "X-Machine-Key")] string? machineKey,
            string code)
        {
            if (!KeyOk(machineKey))
                return Unauthorized(new { Message = "Invalid or missing machine key." });

            var (paired, userName) = _otpServices.GetSessionStatus(code);
            return Ok(new SessionStatusDto { Paired = paired, UserName = userName });
        }

        // The paired user's total point balance — shown on the machine's Summary screen.
        [HttpGet("session/{code}/total")]
        public IActionResult SessionTotal(
            [FromHeader(Name = "X-Machine-Key")] string? machineKey,
            string code)
        {
            if (!KeyOk(machineKey))
                return Unauthorized(new { Message = "Invalid or missing machine key." });

            var userId = _otpServices.GetUserId(code);
            var points = userId == null ? 0 : _rewardServices.GetAvailableCoins(userId);
            return Ok(new { Points = points });
        }

        // The machine ends the session (Finish / idle timeout) -> stop the OTP so the paired
        // phone's poll sees it end and auto-closes too (two-way session close).
        [HttpPost("session/{code}/end")]
        public IActionResult EndMachineSession(
            [FromHeader(Name = "X-Machine-Key")] string? machineKey,
            string code)
        {
            if (!KeyOk(machineKey))
                return Unauthorized(new { Message = "Invalid or missing machine key." });

            var stopped = _otpServices.EndSessionByCode(code);
            return Ok(new { Ended = stopped > 0 });
        }

        // Validate an OTP before the kiosk starts a session (does NOT consume it).
        [HttpGet("Validate")]
        public IActionResult Validate(
            [FromHeader(Name = "X-Machine-Key")] string? machineKey,
            [FromQuery] string otp)
        {
            if (!KeyOk(machineKey))
                return Unauthorized(new { Message = "Invalid or missing machine key." });

            if (_transactionServices.IsOtpValid(otp))
                return Ok(new { Valid = true, Message = "OTP is valid." });

            return BadRequest(new { Valid = false, Message = "Invalid or expired OTP." });
        }

        [HttpPost]
        public IActionResult Submit(
            [FromHeader(Name = "X-Machine-Key")] string? machineKey,
            [FromBody] MachineDetection detection)
        {
            if (!KeyOk(machineKey))
                return Unauthorized(new { Message = "Invalid or missing machine key." });

            try
            {
                var result = _transactionServices.AddMachineDetection(detection);
                return Created(string.Empty, result);
            }
            catch (Exception ex)
            {
                return BadRequest(new { Message = ex.Message });
            }
        }
    }
}
