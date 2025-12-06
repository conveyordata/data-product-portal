package provider

import (
	"testing"

	"github.com/hashicorp/terraform-plugin-testing/helper/resource"
)

func TestAccTagDataSource(t *testing.T) {
	resource.Test(t, resource.TestCase{
		PreCheck:                 func() { testAccPreCheck(t) },
		ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
		Steps: []resource.TestStep{
			{
				// Use a tag from the running backend
				Config: testAccTagDataSourceConfig(),
				Check: resource.ComposeAggregateTestCheckFunc(
					resource.TestCheckResourceAttr("data.dataproductportal_tag.test", "id", "c55739df-7f0d-47b9-87ce-ed7065bc17a3"),
					resource.TestCheckResourceAttr("data.dataproductportal_tag.test", "value", "test-val"),
				),
			},
		},
	})
}

func testAccTagDataSourceConfig() string {
	// Use an existing tag ID from the running backend
	return `
data "dataproductportal_tag" "test" {
  id = "c55739df-7f0d-47b9-87ce-ed7065bc17a3"
}
`
}
