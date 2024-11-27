import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

//Labels for the current change status
export const CURRENT_STATUS = {
  created: "Status Created",
};
