import { format, formatDistanceToNow, parseISO } from 'date-fns';

export enum DateFormat {
    DD_MM_YYYY = 'dd/MM/yyyy',
    DD_MM_YYYY_HH_MM = 'dd/MM/yyyy HH:mm',
    DD_MMM_YYYY = 'do MMM yyyy',
    DD_MMM_YYYY_HH_MM = 'do MMM yyyy HH:mm',
}

export const formatDate = (date: string | number | Date, dateFormat: DateFormat = DateFormat.DD_MMM_YYYY) => {
    return format(date, dateFormat);
};

export const formatDateFromISOString = (date: string, dateFormat: DateFormat = DateFormat.DD_MMM_YYYY) => {
    return formatDate(parseISO(date), dateFormat);
};

export const formatDateToNow = (date: string | number | Date) => {
    return formatDistanceToNow(date, { addSuffix: true });
};

export const formatDateToNowFromISOString = (date: string) => {
    return formatDateToNow(parseISO(date));
};

export const formatDateToNowFromUTCString = (date: string) => {
    return formatDateToNowFromISOString(`${date}Z`);
};
