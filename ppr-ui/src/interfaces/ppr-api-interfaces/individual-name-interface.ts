
// Individual name interface.
export interface IndividualNameIF {
  first: string,
  last: string,
  second?: string, // Optional
  middle?: string, // Optional search debtor uses second; everywhere else uses middle.
}
