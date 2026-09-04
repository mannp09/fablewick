// A reader "stage page" is one screen the reader steps through: the
// cover, one of the book's content pages (art + story text), or the
// closing page. Index is 0-based and only meaningful for 'content'.
export type StagePageKind = 'cover' | 'content' | 'end';

export interface StagePage {
  kind: StagePageKind;
  index: number;
}
