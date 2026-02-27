package provider

import (
	"fmt"
	"testing"

	"github.com/hashicorp/terraform-plugin-testing/helper/resource"
)

func TestAccDomainDataSource_basic(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping acceptance test in short mode")
	}
	testAccPreCheck(t)

	resource.Test(t, resource.TestCase{
		ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
		Steps: []resource.TestStep{
			{
				Config: testAccDomainDataSourceConfig("test-domain-ds", "Domain for data source test"),
				Check: resource.ComposeAggregateTestCheckFunc(
					resource.TestCheckResourceAttr("data.dataproductportal_domain.test", "name", "test-domain-ds"),
					resource.TestCheckResourceAttr("data.dataproductportal_domain.test", "description", "Domain for data source test"),
				),
			},
		},
	})
}

func testAccDomainDataSourceConfig(name, description string) string {
	return fmt.Sprintf(`
provider "dataproductportal" {}

resource "dataproductportal_domain" "source" {
  name        = %[1]q
  description = %[2]q
}

data "dataproductportal_domain" "test" {
  id = dataproductportal_domain.source.id
}
`, name, description)
}
