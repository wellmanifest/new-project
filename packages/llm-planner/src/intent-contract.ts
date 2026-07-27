import {
  INTENT_CONTRACT_DSL_VERSION,
  collectFormalFields,
  createField,
  validateIntentContractDsl,
  type DocumentType,
  type FieldStatus,
  type FormalField,
  type IntentContractDsl,
  type SourceReference
} from "../../intent-contract-model/src/index.js";

export const STRUCTURED_PLANNER_RESPONSE_VERSION = "intent-contract.planner-response.v1";

export type ControlledPlannerSourceKind = "message" | "file" | "system" | "derived";

export interface ControlledPlannerSource {
  id: string;
  kind: ControlledPlannerSourceKind;
  path?: string;
  quote: string;
  span?: { start: number; end: number };
}

export interface ControlledPlannerField {
  path: ControlledPlannerFieldPath;
  value: unknown;
  status: FieldStatus;
  requiredForCompletion: boolean;
  sourceId?: string;
  interpretations?: string[];
}

export interface ControlledPlannerResponse {
  version: typeof STRUCTURED_PLANNER_RESPONSE_VERSION;
  documentId: string;
  contractId: string;
  sources: ControlledPlannerSource[];
  fields: ControlledPlannerField[];
}

export interface ControlledPlannerSchema {
  version: typeof STRUCTURED_PLANNER_RESPONSE_VERSION;
  allowedStatuses: FieldStatus[];
  allowedPaths: ControlledPlannerFieldPath[];
  requiredTopLevelKeys: Array<keyof ControlledPlannerResponse>;
}

export interface ControlledPlannerValidationIssue {
  path: string;
  message: string;
}

export interface ControlledPlannerValidationResult {
  ok: boolean;
  issues: ControlledPlannerValidationIssue[];
}

export interface NaturalLanguagePlannerOptions {
  id?: string;
  language?: string;
  sourceId?: string;
  sourcePath?: string;
}

export interface RenderedStatement {
  id: string;
  dslPath: string;
  field: string;
  text: string;
  sourceId?: string;
}

export interface NaturalLanguageRenderResult {
  version: "intent-contract.nl-summary.v1";
  dslHash: string;
  text: string;
  statements: RenderedStatement[];
}

export type ControlledPlannerFieldPath =
  | "document.type"
  | "document.title"
  | "document.language"
  | "contract.title"
  | "contract.governingLaw"
  | "parties.human1.name"
  | "parties.human2.name"
  | "subjects.scope.description"
  | "obligations.provider.description"
  | "deliverables.primary.description"
  | "payments.primary.total"
  | "deadlines.primary.dueAt"
  | "acceptanceCriteria.primary.description"
  | "exclusions.primary.description"
  | "assumptions.primary.description";

const allowedPaths: ControlledPlannerFieldPath[] = [
  "document.type",
  "document.title",
  "document.language",
  "contract.title",
  "contract.governingLaw",
  "parties.human1.name",
  "parties.human2.name",
  "subjects.scope.description",
  "obligations.provider.description",
  "deliverables.primary.description",
  "payments.primary.total",
  "deadlines.primary.dueAt",
  "acceptanceCriteria.primary.description",
  "exclusions.primary.description",
  "assumptions.primary.description"
];

const allowedStatuses: FieldStatus[] = [
  "CONFIRMED",
  "MISSING",
  "INCOMPLETE",
  "AMBIGUOUS",
  "CONFLICTING",
  "ASSUMED",
  "REJECTED",
  "NOT_APPLICABLE"
];

export const CONTROLLED_PLANNER_SCHEMA: ControlledPlannerSchema = {
  version: STRUCTURED_PLANNER_RESPONSE_VERSION,
  allowedStatuses,
  allowedPaths,
  requiredTopLevelKeys: ["version", "documentId", "contractId", "sources", "fields"]
};

export function buildOpenRouterIntentContractPrompt(inputKind: "message" | "guideline-file"): {
  system: string;
  schema: ControlledPlannerSchema;
} {
  return {
    schema: CONTROLLED_PLANNER_SCHEMA,
    system: [
      "Return only JSON matching intent-contract.planner-response.v1.",
      `Input kind: ${inputKind}.`,
      "Use only allowed field paths and statuses from the supplied schema.",
      "Do not invent parties, money, dates, acceptance criteria, exclusions, or governing law.",
      "Every CONFIRMED material field must cite a sourceId from sources.",
      "Use MISSING for required terms that are needed but absent.",
      "Use ASSUMED only for non-material labels such as titles or default language."
    ].join("\n")
  };
}

export function validateControlledPlannerResponse(
  value: unknown
): ControlledPlannerValidationResult {
  const issues: ControlledPlannerValidationIssue[] = [];
  if (!value || typeof value !== "object") return fail("$", "response must be an object");
  const root = value as Partial<ControlledPlannerResponse>;
  if (root.version !== STRUCTURED_PLANNER_RESPONSE_VERSION) {
    issues.push({ path: "version", message: `must be ${STRUCTURED_PLANNER_RESPONSE_VERSION}` });
  }
  if (!root.documentId || typeof root.documentId !== "string") {
    issues.push({ path: "documentId", message: "is required" });
  }
  if (!root.contractId || typeof root.contractId !== "string") {
    issues.push({ path: "contractId", message: "is required" });
  }
  if (!Array.isArray(root.sources)) issues.push({ path: "sources", message: "must be an array" });
  if (!Array.isArray(root.fields)) issues.push({ path: "fields", message: "must be an array" });

  const sourceIds = new Set<string>();
  root.sources?.forEach((source, index) => {
    const basePath = `sources[${index}]`;
    if (!source || typeof source !== "object") {
      issues.push({ path: basePath, message: "must be an object" });
      return;
    }
    if (!source.id || typeof source.id !== "string") {
      issues.push({ path: `${basePath}.id`, message: "is required" });
    } else if (sourceIds.has(source.id)) {
      issues.push({ path: `${basePath}.id`, message: `duplicate source id ${source.id}` });
    } else {
      sourceIds.add(source.id);
    }
    if (!isSourceKind(source.kind))
      issues.push({ path: `${basePath}.kind`, message: "unknown source kind" });
    if (typeof source.quote !== "string" || !source.quote.trim()) {
      issues.push({ path: `${basePath}.quote`, message: "is required" });
    }
  });

  const seenPaths = new Set<string>();
  root.fields?.forEach((field, index) => {
    const basePath = `fields[${index}]`;
    if (!field || typeof field !== "object") {
      issues.push({ path: basePath, message: "must be an object" });
      return;
    }
    if (!isAllowedPath(field.path)) {
      issues.push({ path: `${basePath}.path`, message: "unknown field path" });
    } else if (seenPaths.has(field.path)) {
      issues.push({ path: `${basePath}.path`, message: `duplicate field path ${field.path}` });
    } else {
      seenPaths.add(field.path);
    }
    if (!allowedStatuses.includes(field.status as FieldStatus)) {
      issues.push({ path: `${basePath}.status`, message: "unknown status" });
    }
    if (typeof field.requiredForCompletion !== "boolean") {
      issues.push({ path: `${basePath}.requiredForCompletion`, message: "must be boolean" });
    }
    if ((field.status === "CONFIRMED" || field.status === "INCOMPLETE") && field.value === null) {
      issues.push({
        path: `${basePath}.value`,
        message: `${field.status} fields must carry a value`
      });
    }
    if (field.requiredForCompletion && field.status === "CONFIRMED" && !field.sourceId) {
      issues.push({
        path: `${basePath}.sourceId`,
        message: "material confirmed fields must cite a source"
      });
    }
    if (field.sourceId && !sourceIds.has(field.sourceId)) {
      issues.push({ path: `${basePath}.sourceId`, message: `unknown source id ${field.sourceId}` });
    }
    if (
      field.path === "document.type" &&
      typeof field.value === "string" &&
      !isDocumentType(field.value)
    ) {
      issues.push({ path: `${basePath}.value`, message: "unknown document type" });
    }
    if (
      field.path === "payments.primary.total" &&
      field.value !== null &&
      !isPaymentValue(field.value)
    ) {
      issues.push({ path: `${basePath}.value`, message: "payment must be { amount, currency }" });
    }
  });
  return { ok: issues.length === 0, issues };

  function fail(path: string, message: string): ControlledPlannerValidationResult {
    return { ok: false, issues: [{ path, message }] };
  }
}

export function parseControlledPlannerResponse(input: string): ControlledPlannerResponse {
  const parsed = JSON.parse(input) as unknown;
  const validation = validateControlledPlannerResponse(parsed);
  if (!validation.ok) {
    throw new Error(validation.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; "));
  }
  return parsed as ControlledPlannerResponse;
}

export function intentContractDslFromPlannerResponse(
  response: ControlledPlannerResponse
): IntentContractDsl {
  const validation = validateControlledPlannerResponse(response);
  if (!validation.ok) {
    throw new Error(validation.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; "));
  }
  const sources = response.sources.map(toSourceReference);
  const sourceById = new Map(sources.map((source) => [source.id, source]));
  const fieldByPath = new Map(response.fields.map((field) => [field.path, field]));
  const systemSource: SourceReference = {
    type: "system",
    id: `${response.documentId}:controlled-planner`,
    quote: "Validated controlled planner response"
  };

  const dsl: IntentContractDsl = {
    version: INTENT_CONTRACT_DSL_VERSION,
    document: {
      id: response.documentId,
      type: typedField<DocumentType>(
        fieldByPath,
        "document.type",
        "SERVICE_AGREEMENT",
        "ASSUMED",
        false,
        systemSource,
        sourceById
      ),
      title: typedField<string>(
        fieldByPath,
        "document.title",
        "Intent/Contract draft",
        "ASSUMED",
        false,
        systemSource,
        sourceById
      ),
      language: typedField<string>(
        fieldByPath,
        "document.language",
        "pl",
        "ASSUMED",
        false,
        systemSource,
        sourceById
      )
    },
    contract: {
      id: response.contractId,
      title: typedField<string>(
        fieldByPath,
        "contract.title",
        "Contract draft",
        "ASSUMED",
        false,
        systemSource,
        sourceById
      ),
      governingLaw: typedField<string>(
        fieldByPath,
        "contract.governingLaw",
        null,
        "MISSING",
        true,
        null,
        sourceById
      )
    },
    parties: [
      {
        id: "human1",
        name: typedField<string>(
          fieldByPath,
          "parties.human1.name",
          "Human1",
          "ASSUMED",
          false,
          systemSource,
          sourceById
        ),
        role: createField("parties.human1.role", "Human1", "CONFIRMED", true, systemSource)
      },
      {
        id: "human2",
        name: typedField<string>(
          fieldByPath,
          "parties.human2.name",
          "Human2",
          "ASSUMED",
          false,
          systemSource,
          sourceById
        ),
        role: createField("parties.human2.role", "Human2", "CONFIRMED", true, systemSource)
      }
    ],
    roles: [
      {
        id: "requester",
        partyId: createField("roles.requester.partyId", "human1", "ASSUMED", false, systemSource),
        name: createField("roles.requester.name", "requester", "ASSUMED", false, systemSource)
      },
      {
        id: "provider",
        partyId: createField("roles.provider.partyId", "human2", "ASSUMED", false, systemSource),
        name: createField("roles.provider.name", "provider", "ASSUMED", false, systemSource)
      }
    ],
    intents: [
      {
        id: "primary-intent",
        requesterPartyId: createField(
          "intents.primary-intent.requesterPartyId",
          "human1",
          "ASSUMED",
          false,
          systemSource
        ),
        description: typedField<string>(
          fieldByPath,
          "subjects.scope.description",
          null,
          "MISSING",
          true,
          null,
          sourceById,
          "intents.primary-intent.description"
        )
      }
    ],
    subjects: [
      {
        id: "scope",
        description: typedField<string>(
          fieldByPath,
          "subjects.scope.description",
          null,
          "MISSING",
          true,
          null,
          sourceById
        )
      }
    ],
    obligations: maybeNode(fieldByPath, "obligations.provider.description", (field) => [
      {
        id: "provider-obligation",
        partyId: createField(
          "obligations.provider-obligation.partyId",
          "human2",
          "ASSUMED",
          false,
          systemSource
        ),
        description: remapField<string>(
          field,
          "obligations.provider-obligation.description",
          sourceById
        )
      }
    ]),
    deliverables: [
      {
        id: "primary",
        description: typedField<string>(
          fieldByPath,
          "deliverables.primary.description",
          null,
          "MISSING",
          true,
          null,
          sourceById
        ),
        ownerPartyId: createField(
          "deliverables.primary.ownerPartyId",
          "human2",
          "ASSUMED",
          false,
          systemSource
        )
      }
    ],
    deadlines: maybeNode(fieldByPath, "deadlines.primary.dueAt", (field) => [
      {
        id: "primary-deadline",
        forId: createField(
          "deadlines.primary-deadline.forId",
          "primary",
          "ASSUMED",
          false,
          systemSource
        ),
        dueAt: remapField<string>(field, "deadlines.primary-deadline.dueAt", sourceById)
      }
    ]),
    payments: maybeNode(fieldByPath, "payments.primary.total", (field) => [
      {
        id: "primary-payment",
        payerPartyId: createField(
          "payments.primary-payment.payerPartyId",
          "human1",
          "ASSUMED",
          false,
          systemSource
        ),
        payeePartyId: createField(
          "payments.primary-payment.payeePartyId",
          "human2",
          "ASSUMED",
          false,
          systemSource
        ),
        total: remapField<{ amount: number; currency: string }>(
          field,
          "payments.primary-payment.total",
          sourceById
        )
      }
    ]),
    conditions: [],
    dependencies: [],
    acceptanceCriteria: maybeNode(
      fieldByPath,
      "acceptanceCriteria.primary.description",
      (field) => [
        {
          id: "primary-acceptance",
          description: remapField<string>(
            field,
            "acceptanceCriteria.primary.description",
            sourceById
          ),
          appliesToId: createField(
            "acceptanceCriteria.primary.appliesToId",
            "primary",
            "ASSUMED",
            false,
            systemSource
          )
        }
      ]
    ),
    exclusions: maybeNode(fieldByPath, "exclusions.primary.description", (field) => [
      {
        id: "primary-exclusion",
        description: remapField<string>(field, "exclusions.primary.description", sourceById)
      }
    ]),
    assumptions: [
      ...maybeNode(fieldByPath, "assumptions.primary.description", (field) => [
        {
          id: "primary-assumption",
          description: remapField<string>(field, "assumptions.primary.description", sourceById)
        }
      ]),
      {
        id: "controlled-planner-boundary",
        description: createField(
          "assumptions.controlled-planner-boundary.description",
          "The DSL was created from a controlled planner response; absent terms remain missing and no external semantics were inferred.",
          "ASSUMED",
          false,
          systemSource
        )
      }
    ],
    risks: [],
    conflicts: [],
    questions: [
      {
        id: "governing-law",
        targetPartyId: createField(
          "questions.governing-law.targetPartyId",
          "human1",
          "ASSUMED",
          true,
          systemSource
        ),
        field: "contract.governingLaw",
        prompt: createField(
          "questions.governing-law.prompt",
          "Provide the governing law for this contract.",
          "MISSING",
          true,
          systemSource
        )
      }
    ],
    approvals: [],
    sourceReferences: [...sources, systemSource],
    render: [
      {
        id: "nl-summary",
        target: createField("render.nl-summary.target", "summary", "ASSUMED", false, systemSource)
      }
    ],
    execution: []
  };

  const dslValidation = validateIntentContractDsl(dsl);
  if (!dslValidation.ok) {
    throw new Error(
      dslValidation.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; ")
    );
  }
  return dsl;
}

export function mockPlanIntentContractFromNaturalLanguage(
  input: string,
  options: NaturalLanguagePlannerOptions = {}
): IntentContractDsl {
  return intentContractDslFromPlannerResponse(
    controlledResponseFromText(input, {
      id: options.id ?? "single-message",
      kind: "message",
      language: options.language ?? detectLanguage(input),
      sourceId: options.sourceId ?? "message-1",
      sourcePath: options.sourcePath
    })
  );
}

export function mockPlanGuidelineFileToIntentContractDsl(
  text: string,
  options: NaturalLanguagePlannerOptions = {}
): IntentContractDsl {
  return intentContractDslFromPlannerResponse(
    controlledResponseFromText(text, {
      id: options.id ?? "guideline-file",
      kind: "file",
      language: options.language ?? detectLanguage(text),
      sourceId: options.sourceId ?? "guidelines-1",
      sourcePath: options.sourcePath ?? "guidelines.md"
    })
  );
}

export function renderIntentContractDslToNaturalLanguage(
  dsl: IntentContractDsl,
  dslHash: string
): NaturalLanguageRenderResult {
  const statements = collectFormalFields(dsl)
    .filter(({ field }) => field.value !== null && field.status !== "NOT_APPLICABLE")
    .map(({ path, field }, index) => ({
      id: `stmt-${String(index + 1).padStart(3, "0")}`,
      dslPath: path,
      field: field.field,
      sourceId: field.source?.id,
      text: `[${path}] ${field.field}: ${formatFieldValue(field.value)} (${field.status}).`
    }));
  return {
    version: "intent-contract.nl-summary.v1",
    dslHash,
    statements,
    text: statements.map((statement) => statement.text).join("\n")
  };
}

export function extractRenderedStatementPaths(text: string): string[] {
  return text
    .split(/\r?\n/)
    .map((line) => /^\[(.+)\]\s/.exec(line.trim())?.[1])
    .filter((path): path is string => Boolean(path));
}

function controlledResponseFromText(
  text: string,
  options: {
    id: string;
    kind: ControlledPlannerSourceKind;
    language: string;
    sourceId: string;
    sourcePath?: string;
  }
): ControlledPlannerResponse {
  const source: ControlledPlannerSource = {
    id: options.sourceId,
    kind: options.kind,
    path: options.sourcePath,
    quote: text,
    span: { start: 0, end: text.length }
  };
  const documentType = classifyDocumentType(text);
  const fields: ControlledPlannerField[] = [
    field("document.type", documentType, "CONFIRMED", true, source.id),
    field("document.title", titleFor(documentType, text), "ASSUMED", false),
    field("document.language", options.language, "ASSUMED", false),
    field("contract.title", titleFor(documentType, text), "ASSUMED", false),
    field("contract.governingLaw", null, "MISSING", true),
    field(
      "parties.human1.name",
      findRequesterName(text) ?? "Human1",
      findRequesterName(text) ? "CONFIRMED" : "ASSUMED",
      false,
      findRequesterName(text) ? source.id : undefined
    ),
    field(
      "parties.human2.name",
      findProviderName(text) ?? "Human2",
      findProviderName(text) ? "CONFIRMED" : "ASSUMED",
      false,
      findProviderName(text) ? source.id : undefined
    ),
    field(
      "subjects.scope.description",
      findScope(text),
      findScope(text) ? "CONFIRMED" : "MISSING",
      true,
      findScope(text) ? source.id : undefined
    ),
    field(
      "deliverables.primary.description",
      findDeliverable(text),
      findDeliverable(text) ? "CONFIRMED" : "MISSING",
      true,
      findDeliverable(text) ? source.id : undefined
    )
  ];
  const obligation = findObligation(text);
  if (obligation)
    fields.push(
      field("obligations.provider.description", obligation, "CONFIRMED", true, source.id)
    );
  const payment = findPaymentValue(text);
  if (payment) fields.push(field("payments.primary.total", payment, "CONFIRMED", true, source.id));
  const deadline = findDateValue(text);
  if (deadline)
    fields.push(field("deadlines.primary.dueAt", deadline, "CONFIRMED", true, source.id));
  const acceptance = findAcceptance(text);
  if (acceptance)
    fields.push(
      field("acceptanceCriteria.primary.description", acceptance, "CONFIRMED", true, source.id)
    );
  const exclusion = findExclusion(text);
  if (exclusion)
    fields.push(field("exclusions.primary.description", exclusion, "CONFIRMED", true, source.id));
  const assumption = findAssumption(text);
  if (assumption)
    fields.push(field("assumptions.primary.description", assumption, "ASSUMED", false, source.id));

  return {
    version: STRUCTURED_PLANNER_RESPONSE_VERSION,
    documentId: `${options.id}:document`,
    contractId: `${options.id}:contract`,
    sources: [source],
    fields
  };
}

function field(
  path: ControlledPlannerFieldPath,
  value: unknown,
  status: FieldStatus,
  requiredForCompletion: boolean,
  sourceId?: string
): ControlledPlannerField {
  return { path, value, status, requiredForCompletion, sourceId };
}

function typedField<T>(
  fieldByPath: Map<ControlledPlannerFieldPath, ControlledPlannerField>,
  path: ControlledPlannerFieldPath,
  fallback: T | null,
  fallbackStatus: FieldStatus,
  fallbackRequired: boolean,
  fallbackSource: SourceReference | null,
  sourceById: Map<string, SourceReference>,
  fieldName: string = path
): FormalField<T> {
  const controlled = fieldByPath.get(path);
  if (!controlled)
    return createField(fieldName, fallback, fallbackStatus, fallbackRequired, fallbackSource);
  return remapField<T>(controlled, fieldName, sourceById);
}

function remapField<T>(
  controlled: ControlledPlannerField,
  fieldName: string,
  sourceById: Map<string, SourceReference>
): FormalField<T> {
  const created = createField(
    fieldName,
    controlled.value as T,
    controlled.status,
    controlled.requiredForCompletion,
    controlled.sourceId ? (sourceById.get(controlled.sourceId) ?? null) : null
  );
  if (controlled.interpretations) created.interpretations = controlled.interpretations;
  return created;
}

function maybeNode<T>(
  fieldByPath: Map<ControlledPlannerFieldPath, ControlledPlannerField>,
  path: ControlledPlannerFieldPath,
  build: (field: ControlledPlannerField) => T[]
): T[] {
  const field = fieldByPath.get(path);
  return field && field.value !== null ? build(field) : [];
}

function toSourceReference(source: ControlledPlannerSource): SourceReference {
  return {
    type: source.kind === "file" ? "file" : source.kind,
    id: source.id,
    path: source.path,
    quote: source.quote,
    span: source.span
  };
}

function isAllowedPath(path: unknown): path is ControlledPlannerFieldPath {
  return typeof path === "string" && allowedPaths.includes(path as ControlledPlannerFieldPath);
}

function isSourceKind(kind: unknown): kind is ControlledPlannerSourceKind {
  return kind === "message" || kind === "file" || kind === "system" || kind === "derived";
}

function isDocumentType(value: string): value is DocumentType {
  return [
    "OFFICE_COMMAND",
    "TASK_DELEGATION",
    "SERVICE_AGREEMENT",
    "EMPLOYMENT_AGREEMENT",
    "CONTRACT",
    "TECHNICAL_SPECIFICATION",
    "IMPLEMENTATION_PLAN"
  ].includes(value);
}

function isPaymentValue(value: unknown): value is { amount: number; currency: string } {
  return Boolean(
    value &&
      typeof value === "object" &&
      typeof (value as { amount?: unknown }).amount === "number" &&
      typeof (value as { currency?: unknown }).currency === "string"
  );
}

function classifyDocumentType(text: string): DocumentType {
  const normalized = text.toLowerCase();
  if (/employment|employee|pracownik|zatrudn|etat/.test(normalized)) return "EMPLOYMENT_AGREEMENT";
  if (/guideline|policy|zasad|wytyczn/.test(normalized)) return "EMPLOYMENT_AGREEMENT";
  if (/delegate|task|zadanie|zlec/.test(normalized)) return "TASK_DELEGATION";
  return "SERVICE_AGREEMENT";
}

function detectLanguage(text: string): string {
  return /\b(the|and|must|shall|service|payment)\b/i.test(text) ? "en" : "pl";
}

function titleFor(type: DocumentType, text: string): string {
  const explicit = /(?:title|tytul|nazwa)[:\s]+([^\n.]+)/i.exec(text)?.[1]?.trim();
  if (explicit) return explicit;
  if (type === "TASK_DELEGATION") return "Task delegation draft";
  if (type === "EMPLOYMENT_AGREEMENT") return "Employment guideline draft";
  return "Service agreement draft";
}

function findRequesterName(text: string): string | null {
  return (
    /(?:client|zamawiajacy|human1)[:\s]+([A-Z][\p{L}-]+(?:\s+[A-Z][\p{L}-]+)?)/iu
      .exec(text)?.[1]
      ?.trim() ?? null
  );
}

function findProviderName(text: string): string | null {
  return (
    /(?:provider|contractor|wykonawca|kandydat|human2)[:\s]+([A-Z][\p{L}-]+(?:\s+[A-Z][\p{L}-]+)?)/iu
      .exec(text)?.[1]
      ?.trim() ?? null
  );
}

function findScope(text: string): string | null {
  return (
    findAfterLabel(text, ["scope", "zakres", "subject", "temat"]) ?? firstMeaningfulSentence(text)
  );
}

function findDeliverable(text: string): string | null {
  return findAfterLabel(text, ["deliverable", "rezultat", "produkt", "output", "wynik"]);
}

function findObligation(text: string): string | null {
  return findAfterLabel(text, ["obligation", "provider must", "wykonawca ma", "zadanie"]);
}

function findAcceptance(text: string): string | null {
  return findAfterLabel(text, ["acceptance", "done when", "kryteria akceptacji", "akceptacja"]);
}

function findExclusion(text: string): string | null {
  return findAfterLabel(text, ["exclusion", "excluded", "wykluczenie", "poza zakresem"]);
}

function findAssumption(text: string): string | null {
  return findAfterLabel(text, ["assumption", "zalozenie"]);
}

function findPaymentValue(text: string): { amount: number; currency: string } | null {
  const match = /(?<amount>\d+(?:[ .]\d+)*)\s*(?<currency>PLN|EUR|USD)/i.exec(text);
  if (!match?.groups) return null;
  return {
    amount: Number(match.groups.amount.replace(/[ .]/g, "")),
    currency: match.groups.currency.toUpperCase()
  };
}

function findDateValue(text: string): string | null {
  return /\b\d{4}-\d{2}-\d{2}\b/.exec(text)?.[0] ?? null;
}

function findAfterLabel(text: string, labels: string[]): string | null {
  for (const label of labels) {
    const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const match = new RegExp(`${escaped}[:\\s-]+([^\\n.]+)`, "iu").exec(text);
    if (match?.[1]?.trim()) return match[1].trim();
  }
  return null;
}

function firstMeaningfulSentence(text: string): string | null {
  const sentence = text
    .split(/[.\n]/)
    .map((part) => part.trim())
    .find((part) => part.length >= 12 && !/^\[[^\]]+\]/.test(part));
  return sentence ?? null;
}

function formatFieldValue(value: unknown): string {
  if (typeof value === "string") return value;
  if (isPaymentValue(value)) return `${value.amount} ${value.currency}`;
  return JSON.stringify(value);
}
