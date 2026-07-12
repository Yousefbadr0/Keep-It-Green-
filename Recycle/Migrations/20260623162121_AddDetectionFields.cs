using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Recycle.Migrations
{
    /// <inheritdoc />
    public partial class AddDetectionFields : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<double>(
                name: "ConfidenceScore",
                table: "Transactions",
                type: "float",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "ImagePath",
                table: "Transactions",
                type: "nvarchar(max)",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "ConfidenceScore",
                table: "Transactions");

            migrationBuilder.DropColumn(
                name: "ImagePath",
                table: "Transactions");
        }
    }
}
