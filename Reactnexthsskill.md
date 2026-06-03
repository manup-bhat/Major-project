---
name: react-nextjs-typescript
description: >
  Comprehensive code review, authoring, and quality guidance for React 19,
  Next.js 15+, and TypeScript projects. Use this skill whenever the user asks
  to write, review, refactor, debug, or audit any React component, Next.js
  page/layout/action, TypeScript module, custom Hook, data-fetching layer,
  form, or state-management code. Also trigger for questions about Hooks rules,
  Server Components, Suspense boundaries, TanStack Query, optimistic updates,
  async patterns, type safety, generics, strict-mode config, ESLint rules, or
  performance optimization. Always consult this skill before producing any
  React/Next.js/TypeScript output — it encodes hard-won patterns that prevent
  silent bugs and regressions.
---

# React · Next.js · TypeScript Skill

A unified, production-grade reference covering React 19, Next.js 15+, and
TypeScript strict-mode patterns. Read the section(s) relevant to the task;
each section is self-contained.

---

## Table of Contents

1. [TypeScript Foundations](#1-typescript-foundations)
2. [React Hooks Rules](#2-react-hooks-rules)
3. [useEffect Patterns](#3-useeffect-patterns)
4. [useMemo / useCallback](#4-usememo--usecallback)
5. [Component Design](#5-component-design)
6. [React 19 — Actions & Forms](#6-react-19--actions--forms)
7. [Suspense & Error Boundaries](#7-suspense--error-boundaries)
8. [Server Components (RSC)](#8-server-components-rsc)
9. [Next.js 15 Patterns](#9-nextjs-15-patterns)
10. [TanStack Query v5](#10-tanstack-query-v5)
11. [Async & Concurrency](#11-async--concurrency)
12. [Immutability & State Shape](#12-immutability--state-shape)
13. [ESLint & tsconfig](#13-eslint--tsconfig)
14. [Master Review Checklist](#14-master-review-checklist)

---

## 1. TypeScript Foundations

### 1.1 Avoid `any` — use `unknown` + type guards

```ts
// ❌ any removes all type safety
function process(data: any) { return data.value; }

// ✅ unknown forces narrowing before use
function process(data: unknown): string {
  if (
    typeof data === 'object' &&
    data !== null &&
    'value' in data &&
    typeof (data as Record<string, unknown>).value === 'string'
  ) {
    return (data as { value: string }).value;
  }
  throw new Error('Invalid data shape');
}
```

### 1.2 Discriminated unions — prefer over optional fields

```ts
// ❌ ambiguous: which fields exist when?
interface ApiState { loading?: boolean; data?: User; error?: Error; }

// ✅ exhaustive and self-documenting
type ApiState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

function render(state: ApiState<User>) {
  switch (state.status) {
    case 'loading': return <Spinner />;
    case 'success': return <View user={state.data} />;  // data: User ✓
    case 'error':   return <Err msg={state.error.message} />;
    case 'idle':    return null;
  }
}
```

### 1.3 `as const` for literal types

```ts
// ❌ method inferred as string — incompatible with fetch overloads
const cfg = { method: 'GET', url: '/api/users' };

// ✅ method inferred as 'GET'
const cfg = { method: 'GET', url: '/api/users' } as const;
fetch(cfg.url, { method: cfg.method });  // no cast needed
```

### 1.4 Generics — constrain, don't over-abstract

```ts
// ✅ keyof constraint gives accurate return type
function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  return keys.reduce((acc, k) => ({ ...acc, [k]: obj[k] }), {} as Pick<T, K>);
}

// ✅ infer for library-style utilities
type Awaited<T> = T extends Promise<infer R> ? R : T;
type UnpackArray<T> = T extends (infer U)[] ? U : T;
```

### 1.5 Essential utility types

```ts
type PartialUser   = Partial<User>;          // all optional
type RequiredUser  = Required<User>;         // all required
type ReadonlyUser  = Readonly<User>;         // no mutation
type UserKeys      = keyof User;             // union of keys
type NameOnly      = Pick<User, 'name'>;     // subset
type WithoutId     = Omit<User, 'id'>;       // exclusion
type UserMap       = Record<string, User>;   // index signature
type NonNullUser   = NonNullable<User | null | undefined>;
```

### 1.6 Template literal & mapped types

```ts
// Type-safe CSS-variable names
type CSSVar = `--${string}`;

// Auto-generate getter names
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};
// Getters<{ name: string }> → { getName: () => string }
```

### 1.7 Narrowing patterns

```ts
// typeof
function len(v: string | string[]) {
  return Array.isArray(v) ? v.length : v.length;
}

// instanceof
function handle(e: unknown) {
  if (e instanceof Error) console.error(e.message);
}

// in operator
function speak(a: Dog | Cat) {
  if ('bark' in a) a.bark(); else a.meow();
}

// Assertion function (throws on failure)
function assertDefined<T>(v: T | null | undefined): asserts v is T {
  if (v == null) throw new Error('Expected value, got null/undefined');
}
```

---

## 2. React Hooks Rules

### Rule 1 — Call Hooks at the top level

```tsx
// ❌ conditional call — React cannot track hook order
function Bad({ show }: { show: boolean }) {
  if (show) {
    const [n, setN] = useState(0);  // Error!
  }
}

// ✅ declare at top, guard with early return
function Good({ show }: { show: boolean }) {
  const [n, setN] = useState(0);
  if (!show) return null;
  return <button onClick={() => setN(n + 1)}>{n}</button>;
}
```

### Rule 2 — Custom Hooks must start with `use`

```tsx
// ❌ not recognized as a Hook by linter
function windowSize() { ... }

// ✅
function useWindowSize() {
  const [size, setSize] = useState({ w: 0, h: 0 });
  useEffect(() => {
    const update = () => setSize({ w: innerWidth, h: innerHeight });
    addEventListener('resize', update);
    update();
    return () => removeEventListener('resize', update);
  }, []);
  return size;
}
```

---

## 3. useEffect Patterns

### 3.1 Complete dependency array — never lie to React

```tsx
// ❌ stale closure: effect uses userId but won't re-run on change
useEffect(() => {
  fetchUser(userId).then(setUser);
}, []);  // missing userId

// ✅ list every reactive value the effect reads
useEffect(() => {
  let cancelled = false;
  fetchUser(userId).then(d => { if (!cancelled) setUser(d); });
  return () => { cancelled = true; };
}, [userId]);
```

### 3.2 Always return a cleanup function for subscriptions / timers

```tsx
useEffect(() => {
  const id = setInterval(() => setTick(t => t + 1), 1_000);
  return () => clearInterval(id);
}, []);

useEffect(() => {
  const ctrl = new AbortController();
  fetch('/api/data', { signal: ctrl.signal }).then(...);
  return () => ctrl.abort();
}, []);
```

### 3.3 Derived state → compute inline (not useEffect)

```tsx
// ❌ extra render cycle, synchronisation risk
const [filtered, setFiltered] = useState<Item[]>([]);
useEffect(() => setFiltered(items.filter(i => i.active)), [items]);

// ✅ computed at render time — no state needed
const filtered = useMemo(() => items.filter(i => i.active), [items]);
```

### 3.4 Event-driven side effects belong in handlers — not effects

```tsx
// ❌ analytics call tied to state change via effect
useEffect(() => { if (query) analytics.track('search', { query }); }, [query]);

// ✅ side effect happens exactly where the event occurs
const handleSearch = (q: string) => {
  setQuery(q);
  analytics.track('search', { query: q });
};
```

### 3.5 `useEffectEvent` (React 19) for non-reactive side effects

```tsx
import { experimental_useEffectEvent as useEffectEvent } from 'react';

function Chat({ roomId, onJoin }: { roomId: string; onJoin: (id: string) => void }) {
  // onJoin is always fresh but NOT a dependency of the effect
  const onJoinStable = useEffectEvent(onJoin);

  useEffect(() => {
    const conn = connect(roomId);
    conn.on('connected', () => onJoinStable(roomId));
    return () => conn.disconnect();
  }, [roomId]);  // onJoin intentionally excluded
}
```

---

## 4. useMemo / useCallback

### 4.1 Only optimize what actually costs something

```tsx
// ❌ memoising a constant object — zero benefit, added noise
const cfg = useMemo(() => ({ timeout: 5_000 }), []);

// ✅ just define it outside the component (stable reference)
const DEFAULT_CFG = { timeout: 5_000 };
```

### 4.2 `useCallback` is only useful when the ref must be stable

```tsx
// ❌ useCallback on a non-memo child: re-creates anyway, wasted
const handle = useCallback(() => console.log('click'), []);
return <PlainDiv onClick={handle} />;

// ✅ necessary when passed to React.memo children or as dep of another hook
const MemoChild = React.memo(({ onClick }: { onClick: () => void }) => (
  <button onClick={onClick}>Click</button>
));

function Parent() {
  const handleClick = useCallback(() => { /* stable ref */ }, []);
  return <MemoChild onClick={handleClick} />;
}
```

### 4.3 `useMemo` + `useCallback` together

```tsx
function Dashboard({ rawData }: { rawData: RawItem[] }) {
  const data = useMemo(() => transformItems(rawData), [rawData]);

  const handleExport = useCallback(() => {
    downloadCSV(data);
  }, [data]);  // re-creates only when data reference changes

  return <MemoizedTable data={data} onExport={handleExport} />;
}
```

### 4.4 Dependency instability anti-pattern

```tsx
// ❌ filters is a new object every render → useCallback is useless
function Bad({ filters }: { filters: Record<string, string> }) {
  const fetch = useCallback(() => fetchItems(filters), [filters]);
}

// ✅ stabilise the input first
function Good({ filters }: { filters: Record<string, string> }) {
  const stableFilters = useMemo(() => filters, [JSON.stringify(filters)]);
  const fetch = useCallback(() => fetchItems(stableFilters), [stableFilters]);
}
```

---

## 5. Component Design

### 5.1 Never define components inside other components

```tsx
// ❌ ChildComponent is a NEW function on every render → remounts every time
function Parent() {
  function Child() { return <div>child</div>; }
  return <Child />;
}

// ✅ define at module scope
function Child() { return <div>child</div>; }
function Parent() { return <Child />; }
```

### 5.2 Stabilise props passed to memoised children

```tsx
// ❌ new object + new function reference every render → memo is useless
<MemoChild style={{ color: 'red' }} onClick={() => {}} />

// ✅
const STYLE = { color: 'red' } as const;
function Parent() {
  const handleClick = useCallback(() => {}, []);
  return <MemoChild style={STYLE} onClick={handleClick} />;
}
```

### 5.3 Single-responsibility & composition

```tsx
// ❌ God component — fetches, formats, validates, renders
function UserDashboard({ id }: { id: string }) {
  // 300 lines ...
}

// ✅ split into focused pieces
function UserDashboard({ id }: { id: string }) {
  return (
    <ErrorBoundary fallback={<ErrorCard />}>
      <Suspense fallback={<DashboardSkeleton />}>
        <UserProfile id={id} />
        <UserActivity id={id} />
      </Suspense>
    </ErrorBoundary>
  );
}
```

### 5.4 Extract logic into custom Hooks

```tsx
// ✅ business logic lives in a Hook, component stays declarative
function useUserProfile(id: string) {
  const query = useSuspenseQuery(userQueryOptions(id));
  const update = useMutation({ mutationFn: updateUser });
  return { user: query.data, update: update.mutate, isPending: update.isPending };
}

function UserProfile({ id }: { id: string }) {
  const { user, update, isPending } = useUserProfile(id);
  return <ProfileForm user={user} onSave={update} saving={isPending} />;
}
```

---

## 6. React 19 — Actions & Forms

### 6.1 `useActionState` — replaces multiple `useState`

```tsx
import { useActionState } from 'react';

// ❌ old pattern — 4 state variables, manual error plumbing
function OldForm() {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState(null);
  const handleSubmit = async (fd: FormData) => { /* ... */ };
}

// ✅ React 19 — state + action + isPending in one hook
type State = { success: boolean; data: unknown; error: string | null };
const INIT: State = { success: false, data: null, error: null };

function NewForm() {
  const [state, action, isPending] = useActionState(
    async (_prev: State, fd: FormData): Promise<State> => {
      try {
        const data = await submitForm(fd);
        return { success: true, data, error: null };
      } catch (e) {
        return { success: false, data: null, error: (e as Error).message };
      }
    },
    INIT
  );

  return (
    <form action={action}>
      <input name="email" type="email" required />
      <button disabled={isPending}>{isPending ? 'Saving…' : 'Submit'}</button>
      {state.error && <p role="alert">{state.error}</p>}
    </form>
  );
}
```

### 6.2 `useFormStatus` — must be inside the `<form>`

```tsx
import { useFormStatus } from 'react-dom';

// ❌ called in the same component as <form> — always returns defaults
function BadForm() {
  const { pending } = useFormStatus();  // ← always false here!
  return <form action={action}><button disabled={pending}>Submit</button></form>;
}

// ✅ extracted child component
function SubmitButton() {
  const { pending } = useFormStatus();  // ← correctly reads parent form
  return <button disabled={pending}>{pending ? 'Saving…' : 'Submit'}</button>;
}

function GoodForm() {
  return (
    <form action={action}>
      <input name="title" />
      <SubmitButton />
    </form>
  );
}
```

### 6.3 `useOptimistic` — instant feedback with automatic rollback

```tsx
import { useOptimistic } from 'react';

function LikeButton({ postId, initialLikes }: { postId: string; initialLikes: number }) {
  const [likes, addOptimistic] = useOptimistic(
    initialLikes,
    (current: number, delta: number) => current + delta
  );

  async function handleLike() {
    addOptimistic(1);           // instant UI update
    await likePost(postId);     // server sync
    // on error React auto-reverts to initialLikes
  }

  return <button onClick={handleLike}>♥ {likes}</button>;
}
```

> **Note:** Do NOT use `useOptimistic` for irreversible operations (payments,
> deletions without undo). Reserve it for low-risk, easily reversible changes.

### 6.4 Server Actions (Next.js 15)

```ts
// actions.ts  ← server-only file
'use server';
import { revalidatePath } from 'next/cache';
import { db } from '@/lib/db';

export async function createPost(
  _prev: { success: boolean; error?: string } | null,
  fd: FormData
) {
  const title = fd.get('title') as string;
  if (!title?.trim()) return { success: false, error: 'Title is required' };
  await db.posts.create({ data: { title } });
  revalidatePath('/posts');
  return { success: true };
}
```

```tsx
// PostForm.tsx
'use client';
import { useActionState } from 'react';
import { createPost } from './actions';

export function PostForm() {
  const [state, action, isPending] = useActionState(createPost, null);
  return (
    <form action={action}>
      <input name="title" />
      <SubmitButton />
      {state?.error && <p role="alert">{state.error}</p>}
    </form>
  );
}
```

---

## 7. Suspense & Error Boundaries

### 7.1 Always pair Suspense with ErrorBoundary

```tsx
// ❌ uncaught error crashes the entire tree
<Suspense fallback={<Spinner />}>
  <AsyncComponent />
</Suspense>

// ✅ every Suspense boundary gets an ErrorBoundary wrapper
<ErrorBoundary fallback={<ErrorCard />}>
  <Suspense fallback={<Skeleton />}>
    <AsyncComponent />
  </Suspense>
</ErrorBoundary>
```

### 7.2 Granular boundaries for independent loading

```tsx
// ❌ one slow component blocks everything
<Suspense fallback={<FullPageSpinner />}>
  <Header />      {/* fast */}
  <MainContent /> {/* slow — holds up Header */}
  <Sidebar />     {/* medium */}
</Suspense>

// ✅ independent boundaries stream independently
export default function Layout() {
  return (
    <>
      <Header />   {/* no boundary needed — synchronous */}
      <div className="grid grid-cols-[1fr_280px]">
        <ErrorBoundary fallback={<ContentError />}>
          <Suspense fallback={<ContentSkeleton />}>
            <MainContent />
          </Suspense>
        </ErrorBoundary>

        <ErrorBoundary fallback={<SidebarError />}>
          <Suspense fallback={<SidebarSkeleton />}>
            <Sidebar />
          </Suspense>
        </ErrorBoundary>
      </div>
    </>
  );
}
```

### 7.3 `use()` hook — consume Promises in Client Components

```tsx
import { use, Suspense } from 'react';

// Parent creates the Promise (doesn't await it)
function Post({ postId }: { postId: string }) {
  const commentsPromise = fetchComments(postId);  // intentionally not awaited
  return (
    <article>
      <PostBody id={postId} />
      <ErrorBoundary fallback={<CommentError />}>
        <Suspense fallback={<CommentsSkeleton />}>
          <Comments promise={commentsPromise} />
        </Suspense>
      </ErrorBoundary>
    </article>
  );
}

// Child reads the Promise — suspends until resolved
function Comments({ promise }: { promise: Promise<Comment[]> }) {
  const comments = use(promise);  // triggers Suspense boundary above
  return <ul>{comments.map(c => <li key={c.id}>{c.text}</li>)}</ul>;
}
```

### 7.4 Meaningful fallbacks — skeletons beat spinners

```tsx
// ❌ generic spinner conveys nothing about the content shape
<Suspense fallback={<div className="spinner" />}>

// ✅ skeleton matches the content's layout → less layout shift
<Suspense fallback={<ArticleCardSkeleton rows={3} />}>
```

---

## 8. Server Components (RSC)

### 8.1 RSC rules

| Allowed in RSC | NOT allowed in RSC |
|---|---|
| `async/await` at top level | `useState`, `useReducer`, `useEffect`, etc. |
| Direct DB / filesystem access | Event handlers (`onClick`, `onChange`) |
| Server-only imports | `'use client'` siblings in same file |
| Pass serialisable props to Client Components | Browser APIs (`window`, `document`) |

### 8.2 Push `'use client'` to leaf nodes

```tsx
// ❌ tainting the layout makes the ENTIRE subtree a client bundle
// app/layout.tsx
'use client';
export default function Layout({ children }) { return <html>{children}</html>; }

// ✅ only the interactive leaf component is a Client Component
// app/components/ThemeToggle.tsx
'use client';
export function ThemeToggle() {
  const [dark, setDark] = useState(false);
  return <button onClick={() => setDark(d => !d)}>{dark ? '🌙' : '☀️'}</button>;
}

// app/layout.tsx — RSC (no directive needed)
import { ThemeToggle } from '@/components/ThemeToggle';
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <ThemeToggle />      {/* Client Component island */}
        <main>{children}</main>
      </body>
    </html>
  );
}
```

### 8.3 Data fetching in RSC — no useEffect required

```tsx
// app/users/page.tsx
import { db } from '@/lib/db';

export default async function UsersPage() {
  const users = await db.users.findMany();  // direct DB call — no API round-trip
  return (
    <section>
      <h1>Users</h1>
      {users.map(u => <UserCard key={u.id} user={u} />)}
    </section>
  );
}
```

### 8.4 Pass Server data into Client islands via props

```tsx
// ✅ Server Component fetches, Client Component handles interaction
// app/posts/[id]/page.tsx  (RSC)
export default async function PostPage({ params }: { params: { id: string } }) {
  const post = await db.posts.findUniqueOrThrow({ where: { id: params.id } });
  return <EditPostForm post={post} />;  // serialised to client via props
}

// components/EditPostForm.tsx  (Client Component)
'use client';
export function EditPostForm({ post }: { post: Post }) {
  const [title, setTitle] = useState(post.title);
  // ...
}
```

---

## 9. Next.js 15 Patterns

### 9.1 App Router file conventions

```
app/
├── layout.tsx          ← RootLayout (RSC)
├── loading.tsx         ← auto Suspense boundary
├── error.tsx           ← auto Error Boundary ('use client')
├── not-found.tsx       ← 404 handler
├── page.tsx            ← route segment (RSC by default)
└── (dashboard)/        ← route group (no URL segment)
    ├── layout.tsx
    └── analytics/
        └── page.tsx
```

### 9.2 Metadata API

```tsx
// Static
export const metadata: Metadata = {
  title: { template: '%s | Acme', default: 'Acme' },
  description: 'Acme — where things happen',
};

// Dynamic
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const product = await fetchProduct(params.id);
  return { title: product.name, openGraph: { images: [product.image] } };
}
```

### 9.3 `params` and `searchParams` are Promises in Next.js 15

```tsx
// ❌ Next.js 14 pattern — breaks in Next.js 15
export default function Page({ params }: { params: { id: string } }) {
  const id = params.id;
}

// ✅ Next.js 15 — params is a Promise
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ tab?: string }>;
}) {
  const { id } = await params;
  const { tab = 'overview' } = await searchParams;
  const data = await fetchProduct(id);
  return <ProductView product={data} defaultTab={tab} />;
}
```

### 9.4 Caching and revalidation

```tsx
// On-demand revalidation (use in Server Actions)
import { revalidatePath, revalidateTag } from 'next/cache';

// Tag-based (preferred)
const posts = await fetch('/api/posts', { next: { tags: ['posts'] } });
// later...
revalidateTag('posts');

// Time-based
export const revalidate = 60;  // seconds — page-level export

// No caching at all
const data = await fetch('/api/live', { cache: 'no-store' });
```

### 9.5 Route Handlers (API routes)

```ts
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;
  const page = Number(searchParams.get('page') ?? '1');
  const users = await db.users.findMany({ skip: (page - 1) * 20, take: 20 });
  return NextResponse.json({ users });
}

export async function POST(req: NextRequest) {
  const body = await req.json() as { name: string; email: string };
  const user = await db.users.create({ data: body });
  return NextResponse.json(user, { status: 201 });
}
```

### 9.6 Middleware

```ts
// middleware.ts  (project root)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(req: NextRequest) {
  const token = req.cookies.get('session')?.value;
  if (!token && req.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', req.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
};
```

---

## 10. TanStack Query v5

### 10.1 Client setup — sane defaults

```tsx
// lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1_000 * 60 * 5,      // 5 min fresh
      gcTime:    1_000 * 60 * 30,     // 30 min GC (was cacheTime in v4)
      retry: 3,
      refetchOnWindowFocus: false,    // tune per project
    },
  },
});
```

### 10.2 `queryOptions` — single source of truth

```tsx
// lib/queries/user.ts
import { queryOptions } from '@tanstack/react-query';

export const userQueryOptions = (id: string) =>
  queryOptions({
    queryKey: ['users', id],
    queryFn:  () => fetchUser(id),
    staleTime: 1_000 * 60 * 2,
  });

// Component
const { data } = useQuery(userQueryOptions(userId));

// Prefetch in loader / RSC
await queryClient.prefetchQuery(userQueryOptions(userId));

// getQueryData is now fully typed
const cached = queryClient.getQueryData(userQueryOptions(userId).queryKey);
```

### 10.3 queryKey must contain every variable that affects the result

```tsx
// ❌ filters change but queryKey is static → stale data shown
useQuery({
  queryKey: ['items'],
  queryFn:  () => fetchItems(filters),
});

// ✅
useQuery({
  queryKey: ['items', filters],   // filters is part of cache identity
  queryFn:  () => fetchItems(filters),
});
```

### 10.4 `useSuspenseQuery` — differences from `useQuery`

| Feature | `useQuery` | `useSuspenseQuery` |
|---|---|---|
| `enabled` option | ✅ | ❌ not supported |
| `placeholderData` | ✅ | ❌ not supported |
| `data` type | `T \| undefined` | `T` (guaranteed) |
| Loading state | `isPending` prop | suspends to boundary |
| Error state | `error` prop | throws to ErrorBoundary |

```tsx
// ✅ conditional query with useSuspenseQuery — use component composition
function UserProfile({ userId }: { userId: string }) {
  // data is T — never undefined inside this component
  const { data: user } = useSuspenseQuery(userQueryOptions(userId));
  return <Profile user={user} />;
}

function UserSection({ userId }: { userId?: string }) {
  if (!userId) return <EmptyState />;      // guard BEFORE Suspense
  return (
    <ErrorBoundary fallback={<UserError />}>
      <Suspense fallback={<UserSkeleton />}>
        <UserProfile userId={userId} />
      </Suspense>
    </ErrorBoundary>
  );
}
```

### 10.5 Mutations — invalidate on success

```tsx
const mutation = useMutation({
  mutationFn: (data: CreatePostInput) => createPost(data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['posts'] });
  },
  onError: (err) => {
    toast.error(`Failed: ${err.message}`);
  },
});
```

### 10.6 Optimistic mutations (v5 `variables` pattern)

```tsx
// ✅ simpler than manual cache manipulation
function TodoList() {
  const { data: todos } = useQuery(todosQueryOptions);
  const { mutate, isPending, variables } = useMutation({
    mutationFn: addTodo,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['todos'] }),
  });

  return (
    <ul>
      {todos?.map(t => <TodoItem key={t.id} todo={t} />)}
      {isPending && (
        <TodoItem todo={variables} isOptimistic className="opacity-60" />
      )}
    </ul>
  );
}
```

### 10.7 v5 loading state fields

```ts
const { isPending, isFetching, isLoading } = useQuery({ ... });
// isPending  → no data in cache yet
// isFetching → a request is in-flight (including background refetches)
// isLoading  → isPending && isFetching (first load)
```

---

## 11. Async & Concurrency

### 11.1 Always handle fetch errors + check `response.ok`

```ts
async function fetchUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
  return res.json() as Promise<User>;
}
```

### 11.2 `Promise.all` vs `Promise.allSettled`

```ts
// Promise.all — use when ALL must succeed
const [user, posts] = await Promise.all([fetchUser(id), fetchPosts(id)]);

// Promise.allSettled — use when partial success is OK
const results = await Promise.allSettled(ids.map(fetchUser));
const users  = results.filter(r => r.status === 'fulfilled').map(r => r.value);
const errors = results.filter(r => r.status === 'rejected').map(r => r.reason);
```

### 11.3 Race conditions — AbortController

```tsx
useEffect(() => {
  const ctrl = new AbortController();
  async function load() {
    try {
      const data = await fetchSearch(query, ctrl.signal);
      setResults(data);
    } catch (e) {
      if ((e as Error).name !== 'AbortError') setError(e as Error);
    }
  }
  void load();
  return () => ctrl.abort();
}, [query]);
```

### 11.4 No `forEach` with `async` — use `for...of` or `Promise.all`

```ts
// ❌ forEach ignores returned Promises → unhandled rejections
items.forEach(async item => await save(item));

// ✅ sequential
for (const item of items) await save(item);

// ✅ parallel
await Promise.all(items.map(save));
```

### 11.5 `no-floating-promises` fixes

```ts
// ❌ ESLint error: floating promise
doAsync();

// ✅ await it
await doAsync();
// ✅ explicitly fire-and-forget
void doAsync();
// ✅ handle inline
doAsync().catch(console.error);
```

---

## 12. Immutability & State Shape

### 12.1 Never mutate props or function arguments

```ts
// ❌ mutates the caller's array
function sort(items: User[]) {
  return items.sort((a, b) => a.name.localeCompare(b.name));
}

// ✅ copy first
function sort(items: readonly User[]): User[] {
  return [...items].sort((a, b) => a.name.localeCompare(b.name));
}
```

### 12.2 `useReducer` for complex state transitions

```tsx
type State = { count: number; history: number[] };
type Action = { type: 'INC' } | { type: 'DEC' } | { type: 'RESET' };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'INC':   return { count: state.count + 1, history: [...state.history, state.count + 1] };
    case 'DEC':   return { count: state.count - 1, history: [...state.history, state.count - 1] };
    case 'RESET': return { count: 0, history: [] };
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, { count: 0, history: [] });
  return (
    <div>
      <span>{state.count}</span>
      <button onClick={() => dispatch({ type: 'INC' })}>+</button>
    </div>
  );
}
```

### 12.3 Prefer derived state over stored state

```tsx
// ❌ redundant: total can always be derived
const [items, setItems] = useState<Item[]>([]);
const [total, setTotal] = useState(0);

// ✅ single source of truth
const [items, setItems] = useState<Item[]>([]);
const total = items.reduce((sum, i) => sum + i.price, 0);  // derived
```

---

## 13. ESLint & tsconfig

### 13.1 Recommended `tsconfig.json`

```jsonc
{
  "compilerOptions": {
    // Strictness
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "useUnknownInCatchVariables": true,

    // Module
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,

    // Output
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "preserve",
    "noEmit": true,

    // Quality
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true
  }
}
```

### 13.2 Recommended ESLint config (flat config style)

```ts
// eslint.config.ts
import tseslint from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import reactHooks from 'eslint-plugin-react-hooks';

export default [
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: { parser: tsParser, parserOptions: { project: true } },
    plugins: {
      '@typescript-eslint': tseslint,
      'react-hooks': reactHooks,
    },
    rules: {
      // Type safety
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unsafe-assignment': 'error',
      '@typescript-eslint/no-unsafe-member-access': 'error',
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-misused-promises': 'error',
      '@typescript-eslint/await-thenable': 'error',

      // Style
      '@typescript-eslint/consistent-type-imports': 'error',
      '@typescript-eslint/prefer-nullish-coalescing': 'warn',
      '@typescript-eslint/prefer-optional-chain': 'warn',

      // Hooks
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
    },
  },
];
```

---

## 14. Master Review Checklist

Use this checklist when reviewing or producing React/Next.js/TypeScript code.

### TypeScript

- [ ] No `any` — use `unknown` + type guard, or proper interface
- [ ] Discriminated unions used for multi-state shapes
- [ ] Generics have `extends` constraints where needed
- [ ] `as const` used for fixed config / option objects
- [ ] No `@ts-ignore` — use `@ts-expect-error` with comment
- [ ] `tsconfig.json` has `"strict": true` and `"noUncheckedIndexedAccess": true`
- [ ] Arrays from index access checked for `undefined` before use

### React Hooks

- [ ] All Hooks called unconditionally at component top level
- [ ] Custom Hooks start with `use`
- [ ] `useEffect` dependency arrays are complete (no suppressed lint warnings)
- [ ] Every `useEffect` with subscriptions/timers returns a cleanup function
- [ ] Derived state computed inline or with `useMemo` — not stored in `useState`
- [ ] Side effects triggered by events live in handlers, not effects
- [ ] `useMemo`/`useCallback` only wraps genuinely expensive or ref-sensitive code

### Component Design

- [ ] No child component definitions inside parent render functions
- [ ] Props passed to `React.memo` children use stable references
- [ ] Components are ≤ 200 lines; logic extracted to custom Hooks
- [ ] Long lists use virtualisation (`react-virtual`, `tanstack-virtual`)

### React 19 / Forms

- [ ] `useActionState` replaces multi-`useState` form patterns
- [ ] `useFormStatus` is called inside a child of `<form>`, not in the form itself
- [ ] `useOptimistic` not used for irreversible operations
- [ ] Server Actions marked `'use server'`, validated on server side

### Suspense & Error Boundaries

- [ ] Every `<Suspense>` is wrapped in an `<ErrorBoundary>`
- [ ] Boundaries are granular — independent content has independent boundaries
- [ ] Fallbacks are skeletons matching content shape, not generic spinners
- [ ] `useSuspenseQuery` is NOT given an `enabled` option — use component guard instead

### RSC / Next.js

- [ ] `'use client'` only on leaf components that actually need interactivity
- [ ] Server Components perform data fetching; Client Components handle interaction
- [ ] `params`/`searchParams` are `await`ed (Next.js 15 async API)
- [ ] Slow data fetches are not blocking the root layout — push them into nested segments

### TanStack Query

- [ ] `queryKey` includes every variable that affects the result
- [ ] `staleTime` is set explicitly (not left at default `0`)
- [ ] Mutations call `invalidateQueries` (or `setQueryData`) on success
- [ ] `useSuspenseQuery` wrapped in `<ErrorBoundary>` + `<Suspense>`
- [ ] `isPending` (no data) vs `isFetching` (in-flight) distinction understood

### Async / Concurrency

- [ ] `fetch` calls check `response.ok` before parsing body
- [ ] Concurrent independent requests use `Promise.all`
- [ ] Race conditions in `useEffect` handled with `AbortController`
- [ ] No `forEach` with `async` callbacks — use `for...of` or `Promise.all`
- [ ] No floating Promises (use `await`, `void`, or `.catch()`)

### Immutability & State

- [ ] Function parameters not mutated; spread used to create new objects/arrays
- [ ] `useReducer` used for state with multiple sub-fields or complex transitions
- [ ] No redundant state — derivable values are derived, not stored

### ESLint

- [ ] `@typescript-eslint/recommended` + `react-hooks` plugin active
- [ ] Zero lint errors in CI; warnings reviewed not ignored
- [ ] `consistent-type-imports` enabled (import type vs value)

---

*Maintained for React 19 · Next.js 15 · TypeScript 5.x · TanStack Query v5.*
