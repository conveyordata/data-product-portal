export interface TagContract {
    id: string;
    value: string;
    rolled_up?: boolean;
}

export interface TagModel extends TagContract {}
