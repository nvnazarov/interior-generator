export const MAX_AVATAR_FILE_SIZE_BYTES = 512 * 1024;

/**
 * Converts person's full name to initials.
 *
 * @param name - Person's full name
 * @returns The intials corresponding to the name
 *
 * @example
 * initials("Peter Parker") === "PP"
 * initials("Peter") === "PE"
 */
export function initials(name: string): string {
  name = name.toUpperCase();
  const parts = name.split(/\s+/);
  if (parts.length < 2) {
    return name.slice(0, 2);
  }
  return parts[0]![0]! + parts[1]![0]!;
}
