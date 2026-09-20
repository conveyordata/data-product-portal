import { STATIC_TAG_ID, TagTypes } from '@/store/api/services/tag-types.ts';

// A graph is a neighbourhood view: linking A to B changes the graph rendered for
// A, for B and for everything already connected to them. Per-entity granularity
// would therefore never be correct, so every graph query shares a single tag and
// any change to the topology invalidates all of them.
export const graphTag = { type: TagTypes.Graph, id: STATIC_TAG_ID.LIST } as const;

export const providesGraphData = { providesTags: [graphTag] };
