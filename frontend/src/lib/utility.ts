import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export const cn = (...inputs: ClassValue[]): string => {
	return twMerge(clsx(inputs));
};

export function lengthToTime(length: number): string {
	const minutes = Math.floor(length / 60);
	const seconds = Math.round(length % 60);
	return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
}

export function capitalize(str: string): string {
	return str
		.split(" ")
		.map((w) => w.substring(0, 1).toUpperCase() + w.substring(1))
		.join(" ");
}
