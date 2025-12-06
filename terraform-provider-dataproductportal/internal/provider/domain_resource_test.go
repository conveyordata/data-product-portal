package provider

import (
	"fmt"
	"testing"

	"github.com/hashicorp/terraform-plugin-testing/helper/resource"
)

func TestAccDomainResource_basic(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping acceptance test in short mode")
	}
	testAccPreCheck(t)

	resource.Test(t, resource.TestCase{
		ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
		Steps: []resource.TestStep{
			// Create and Read testing
			{
				Config: testAccDomainResourceConfig("test-domain-tf", "Test domain from Terraform"),
				Check: resource.ComposeAggregateTestCheckFunc(
					resource.TestCheckResourceAttr("dataproductportal_domain.test", "name", "test-domain-tf"),
					resource.TestCheckResourceAttr("dataproductportal_domain.test", "description", "Test domain from Terraform"),
					resource.TestCheckResourceAttrSet("dataproductportal_domain.test", "id"),
				),
			},
			// ImportState testing
			{
				ResourceName:      "dataproductportal_domain.test",
				ImportState:       true,
				ImportStateVerify: true,
			},
			// Update and Read testing
			{
				Config: testAccDomainResourceConfig("test-domain-tf-updated", "Updated description"),
				Check: resource.ComposeAggregateTestCheckFunc(
					resource.TestCheckResourceAttr("dataproductportal_domain.test", "name", "test-domain-tf-updated"),
					resource.TestCheckResourceAttr("dataproductportal_domain.test", "description", "Updated description"),
				),
			},
			// Delete testing is automatic
		},
	})
}

func TestAccDomainResource_minimal(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping acceptance test in short mode")
	}
	testAccPreCheck(t)

	resource.Test(t, resource.TestCase{
		ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
		Steps: []resource.TestStep{
			{
				// API requires description, so we provide an empty one
				Config: testAccDomainResourceConfig("minimal-domain-tf", "Minimal description"),
				Check: resource.ComposeAggregateTestCheckFunc(
					resource.TestCheckResourceAttr("dataproductportal_domain.test", "name", "minimal-domain-tf"),
					resource.TestCheckResourceAttrSet("dataproductportal_domain.test", "id"),
				),
			},
		},
	})
}

func testAccDomainResourceConfig(name, description string) string {
	return fmt.Sprintf(`
provider "dataproductportal" {}

resource "dataproductportal_domain" "test" {
  name        = %[1]q
  description = %[2]q
}
`, name, description)
}
