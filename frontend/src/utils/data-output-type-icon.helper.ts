import s3BorderIcon from '@/assets/icons/s3-border-icon.svg?react'
import glueBorderIcon from '@/assets/icons/glue-border-icon.svg?react'
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice'

export function getDataOutputIcon(configuration_type: string) {
    switch(configuration_type) {
        case "GlueDataOutput":
            return glueBorderIcon
        case "S3DataOutput":
            return s3BorderIcon
    }
}
