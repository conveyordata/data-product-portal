package provider

import (
	"fmt"
	"testing"

	"github.com/hashicorp/terraform-plugin-testing/helper/resource"
)

func TestAccTagResource_basic(t *testing.T) {
	// Skip: The tags API does not support GET by ID, which is required for resource Read.
	// Tags can be created but cannot be read back individually, only listed.
	// Use the tag data source to read existing tags.
	t.Skip("skipping: tags API does not support GET by ID")

	if testing.Short() {
		t.Skip("skipping acceptance test in short mode")
	}
	testAccPreCheck(t)

	resource.Test(t, resource.TestCase{
		ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
		Steps: []resource.TestStep{
			// Create and Read testing
			{
				Config: testAccTagResourceConfig("test-tag-tf"),
				Check: resource.ComposeAggregateTestCheckFunc(
					resource.TestCheckResourceAttr("dataproductportal_tag.test", "value", "test-tag-tf"),
					resource.TestCheckResourceAttrSet("dataproductportal_tag.test", "id"),
				),
			},
			// Update and Read testing
			{
				Config: testAccTagResourceConfig("test-tag-tf-updated"),
				Check: resource.ComposeAggregateTestCheckFunc(
					resource.TestCheckResourceAttr("dataproductportal_tag.test", "value", "test-tag-tf-updated"),
				),
			},
			// Delete testing is automatic
		},
	})
}

func testAccTagResourceConfig(value string) string {
	return fmt.Sprintf(`
provider "dataproductportal" {}

resource "dataproductportal_tag" "test" {
  value = %[1]q
}
`, value)
}
