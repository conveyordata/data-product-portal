import { DataProductSettingContract } from "@/types/data-product-setting";
import { Flex } from "antd";

type Props = {
    settings: DataProductSettingContract | undefined
};

export function DataProductSettings({ settings }: Props) {

    settings.map()

    return <Flex>
        {settings_comp}
    </Flex>
}
