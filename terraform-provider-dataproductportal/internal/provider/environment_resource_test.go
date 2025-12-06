package provider

import (
	"fmt"
	"testing"

	"github.com/hashicorp/terraform-plugin-testing/helper/resource"
)

func TestAccEnvironmentResource_basic(t *testing.T) {
	// Skip: The environments API does not support POST/PUT/DELETE operations.
	// Environments are read-only resources in the current API version.
	// Use the environment data source to read existing environments.
	t.Skip("skipping: environments API is read-only (no POST/PUT/DELETE)")

	if testing.Short() {
		t.Skip("skipping acceptance test in short mode")
	}
	testAccPreCheck(t)

	resource.Test(t, resource.TestCase{
		ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
		Steps: []resource.TestStep{
			// Create and Read testing
			{
				Config: testAccEnvironmentResourceConfig("test-env-tf", "tst", "test_context"),
				Check: resource.ComposeAggregateTestCheckFunc(
					resource.TestCheckResourceAttr("dataproductportal_environment.test", "name", "test-env-tf"),
					resource.TestCheckResourceAttr("dataproductportal_environment.test", "acronym", "tst"),
					resource.TestCheckResourceAttr("dataproductportal_environment.test", "context", "test_context"),
					resource.TestCheckResourceAttrSet("dataproductportal_environment.test", "id"),
				),
			},
			// Update and Read testing
			{
				Config: testAccEnvironmentResourceConfig("test-env-tf-updated", "upd", "updated_context"),
				Check: resource.ComposeAggregateTestCheckFunc(
					resource.TestCheckResourceAttr("dataproductportal_environment.test", "name", "test-env-tf-updated"),
					resource.TestCheckResourceAttr("dataproductportal_environment.test", "acronym", "upd"),
				),
			},
			// Delete testing is automatic
		},
	})
}

func testAccEnvironmentResourceConfig(name, acronym, context string) string {
	return fmt.Sprintf(`
provider "dataproductportal" {}

resource "dataproductportal_environment" "test" {
  name    = %[1]q
  acronym = %[2]q
  context = %[3]q
}
`, name, acronym, context)
}
