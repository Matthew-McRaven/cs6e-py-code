from typing import List, Type, cast, TypeVar, Generic, Set, Protocol


class TokenProducer[T](Protocol):

    def __next__(self) -> T: ...


T = TypeVar("T")


class ParserBuffer(Generic[T]):
    def __init__(self, producer: TokenProducer[T]):
        self._producer = producer
        self._buffer: List[T] = []

    def peek(self) -> T | None:
        if len(self._buffer) == 0:
            try:
                self._buffer.append(next(self._producer))
            except StopIteration:
                return None
        return self._buffer[0]

    def push(self, value: T):
        self._buffer.append(value)

    def may_match[T](self, expected: Type[T]) -> T | None:
        if (token := self.peek()) and type(token) is expected:
            return cast(T, self._buffer.pop(0))
        return None

    def must_match[T](self, expected: Type[T]) -> T:
        if ret := self.may_match(expected):
            return ret
        raise SyntaxError()

    def skip_to_next_line[T](self, eol_markers: Set[T]):
        while (
            type(token := self.peek()) not in eol_markers and token is not None
        ):
            self._buffer.pop(0)
        # Consume trailing EOL, so we can begin parsing on the next line
        if len(self._buffer) and type(self._buffer[0]) in eol_markers:
            self._buffer.pop(0)
