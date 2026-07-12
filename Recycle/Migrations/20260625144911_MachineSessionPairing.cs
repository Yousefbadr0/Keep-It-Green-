using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Recycle.Migrations
{
    /// <inheritdoc />
    public partial class MachineSessionPairing : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Otps_AspNetUsers_UserId",
                table: "Otps");

            migrationBuilder.AlterColumn<string>(
                name: "UserId",
                table: "Otps",
                type: "nvarchar(450)",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AddForeignKey(
                name: "FK_Otps_AspNetUsers_UserId",
                table: "Otps",
                column: "UserId",
                principalTable: "AspNetUsers",
                principalColumn: "Id");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Otps_AspNetUsers_UserId",
                table: "Otps");

            migrationBuilder.AlterColumn<string>(
                name: "UserId",
                table: "Otps",
                type: "nvarchar(450)",
                nullable: false,
                defaultValue: "",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true);

            migrationBuilder.AddForeignKey(
                name: "FK_Otps_AspNetUsers_UserId",
                table: "Otps",
                column: "UserId",
                principalTable: "AspNetUsers",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);
        }
    }
}
