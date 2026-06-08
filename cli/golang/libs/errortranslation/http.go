package errortranslation

import (
	"fmt"
	"strings"

	"portal/pkg/api"
)

func TranslateHttpError(r *api.HTTPValidationError) error {
	msgs := make([]string, len(r.Detail))
	for i, d := range r.Detail {
		msgs[i] = d.Msg
	}
	return fmt.Errorf("validation error: %s", strings.Join(msgs, "; "))
}
