import type { components } from "./schema";

type Schemas = components["schemas"];

export type Agent = Schemas["AgentResponse"];
export type AgentCreate = Schemas["AgentCreate"];
export type AgentUpdate = Schemas["AgentUpdate"];
export type AgentStats = Schemas["AgentStats"];
export type Call = Schemas["CallResponse"];
export type TranscriptLine = Schemas["TranscriptLineSchema"];
export type Catalogs = Schemas["Catalogs"];
export type KlevaUser = Schemas["KlevaUserResponse"];
export type Token = Schemas["Token"];
export type ValidationErrorItem = Schemas["ValidationError"];
