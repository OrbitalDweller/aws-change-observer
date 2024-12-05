import * as z from "zod";

export const markerFormSchema = z.object({
  name: z.string().min(1, "Name is required"),
  coordinate: z.object({
    latitude: z.string().regex(/^-?\d*\.?\d+$/, "Invalid latitude format"),
    longitude: z.string().regex(/^-?\d*\.?\d+$/, "Invalid longitude format"),
  }),
  subscribedEmails: z
    .array(z.string().email("Invalid email format"))
    .default([]),
});
