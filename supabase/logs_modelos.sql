-- Registro de consultas y predicciones de los modelos M01, M02 y M03.
-- Ejecutar una sola vez en el SQL Editor de Supabase.
--
-- La aplicación usa la clave "anon", por lo que RLS queda habilitado y solo se
-- permite INSERT (no SELECT) sobre estas tablas desde el cliente.

do $$
declare
    modelo text;
begin
    foreach modelo in array array['m01', 'm02', 'm03'] loop
        execute format($tabla$
            create table if not exists public.logs_%1$s (
                id_ejecucion uuid primary key,
                creado_en    timestamptz not null default now(),
                modelo       text not null,
                endpoint     text not null,
                metodo       text not null,
                entrada      jsonb,
                salida       jsonb,
                estado       integer not null,
                error        text,
                duracion_ms  integer
            )
        $tabla$, modelo);

        execute format(
            'alter table public.logs_%s enable row level security',
            modelo
        );

        execute format(
            'drop policy if exists "insert_anon" on public.logs_%s',
            modelo
        );

        execute format(
            'create policy "insert_anon" on public.logs_%s '
            'for insert to anon with check (true)',
            modelo
        );

        execute format(
            'grant insert on table public.logs_%s to anon',
            modelo
        );

        execute format(
            'create index if not exists logs_%s_creado_en_idx '
            'on public.logs_%s (creado_en desc)',
            modelo, modelo
        );
    end loop;
end $$;
