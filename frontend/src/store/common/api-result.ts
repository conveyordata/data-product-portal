interface SQLAlchemyParseError {
    type: string;
    msg: string;
    input: string;
    loc: string[];
    ctx: {
        error: string;
    };
    url: string;
}

export interface ApiError {
    correlation_id?: string;
    detail?: string | SQLAlchemyParseError[];
}
