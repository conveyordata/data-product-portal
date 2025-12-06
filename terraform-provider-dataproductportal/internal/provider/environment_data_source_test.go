package provider

import (
	"testing"

	"github.com/hashicorp/terraform-plugin-testing/helper/resource"
)

func TestAccEnvironmentDataSource(t *testing.T) {
	resource.Test(t, resource.TestCase{
		PreCheck:                 func() { testAccPreCheck(t) },
		ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
		Steps: []resource.TestStep{
			{
				// Use the development environment from sample data
				Config: testAccEnvironmentDataSourceConfig(),
				Check: resource.ComposeAggregateTestCheckFunc(
					resource.TestCheckResourceAttr("data.dataproductportal_environment.test", "id", "1076b245-3b96-41d0-ad28-7d79b5e25bba"),
					resource.TestCheckResourceAttr("data.dataproductportal_environment.test", "name", "development"),
					resource.TestCheckResourceAttr("data.dataproductportal_environment.test", "acronym", "dev"),
					resource.TestCheckResourceAttr("data.dataproductportal_environment.test", "context", "dev_context"),
					resource.TestCheckResourceAttr("data.dataproductportal_environment.test", "is_default", "true"),
				),
			},
		},
	})
}

func testAccEnvironmentDataSourceConfig() string {
	// Use the development environment ID from the running backend
	return `
data "dataproductportal_environment" "test" {
  id = "1076b245-3b96-41d0-ad28-7d79b5e25bba"
}
`
}
