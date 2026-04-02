# From claw-code: src/runtime.py, lines ~89-167 + src/query_engine.py, lines ~61-132
# Layer 1: The Agent Loop — How the harness orchestrates model interactions
# https://github.com/instructkr/claw-code

# --- Part A: The Turn Loop (runtime.py) ---

class PortRuntime:
    def run_turn_loop(self, prompt, max_turns=3):     # ← Bounded loop, NOT while(true)
        engine = QueryEnginePort.from_workspace()      # ← Fresh engine per loop
        matches = self.route_prompt(prompt)             # ← Pre-LLM intelligence: decide which tools matter
        command_names = tuple(m.name for m in matches if m.kind == 'command')
        tool_names = tuple(m.name for m in matches if m.kind == 'tool')
        results = []

        for turn in range(max_turns):                  # ← The core loop: iterate up to max_turns
            turn_prompt = prompt if turn == 0 else f'{prompt} [turn {turn + 1}]'
            result = engine.submit_message(            # ← Each turn submits to the query engine
                turn_prompt, command_names, tool_names, ()
            )
            results.append(result)
            if result.stop_reason != 'completed':      # ← Stop early on budget/error/max_turns
                break
        return results

    def route_prompt(self, prompt, limit=5):           # ← Pre-LLM routing: score tools by token overlap
        tokens = {t.lower() for t in prompt.replace('/', ' ').split() if t}
        matches = []
        for kind, modules in [('command', PORTED_COMMANDS), ('tool', PORTED_TOOLS)]:
            for module in modules:
                score = sum(1 for t in tokens if t in module.name.lower())
                if score > 0:
                    matches.append(RoutedMatch(kind, module.name, module.source_hint, score))
        return sorted(matches, key=lambda m: -m.score)[:limit]


# --- Part B: The Message Pipeline (query_engine.py) ---

class QueryEnginePort:
    def submit_message(self, prompt, matched_commands=(), matched_tools=(), denied_tools=()):
        if len(self.mutable_messages) >= self.config.max_turns:
            return TurnResult(                          # ← Guard: prevent infinite loops
                prompt=prompt, output='Max turns reached',
                matched_commands=matched_commands, matched_tools=matched_tools,
                permission_denials=denied_tools, usage=self.total_usage,
                stop_reason='max_turns_reached')

        output = self._format_output(summary_lines)
        projected_usage = self.total_usage.add_turn(prompt, output)  # ← Track token budget
        stop_reason = 'completed'

        if projected_usage.input_tokens + projected_usage.output_tokens > self.config.max_budget_tokens:
            stop_reason = 'max_budget_reached'         # ← Budget gate: stop if cost exceeds limit

        self.mutable_messages.append(prompt)           # ← Accumulate conversation history
        self.transcript_store.append(prompt)           # ← Persist to transcript
        self.compact_messages_if_needed()              # ← Trigger compaction if history too long
        return TurnResult(prompt=prompt, output=output, stop_reason=stop_reason, ...)

    def stream_submit_message(self, prompt, **kwargs): # ← Streaming variant uses generators
        yield {'type': 'message_start', 'session_id': self.session_id}
        if kwargs.get('matched_commands'):
            yield {'type': 'command_match', 'commands': kwargs['matched_commands']}
        if kwargs.get('matched_tools'):
            yield {'type': 'tool_match', 'tools': kwargs['matched_tools']}
        if kwargs.get('denied_tools'):
            yield {'type': 'permission_denial', 'denials': [d.tool_name for d in kwargs['denied_tools']]}
        result = self.submit_message(prompt, **kwargs)
        yield {'type': 'message_delta', 'text': result.output}
        yield {'type': 'message_stop', 'stop_reason': result.stop_reason}  # ← Final event with stop reason
