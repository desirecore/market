// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package event

import (
	"regexp"
	"sort"
	"strings"
)

// EventFilter decides whether an event should be processed.
type EventFilter interface {
	Allow(eventType string) bool
}

// FilterChain combines multiple filters with AND logic.
type FilterChain struct {
	filters []EventFilter
}

// NewFilterChain creates a filter chain. Nil filters are skipped.
func NewFilterChain(filters ...EventFilter) *FilterChain {
	var valid []EventFilter
	for _, f := range filters {
		if f != nil {
			valid = append(valid, f)
		}
	}
	return &FilterChain{filters: valid}
}

// Allow returns true when all filters pass. An empty chain allows all events.
func (c *FilterChain) Allow(eventType string) bool {
	if c == nil {
		return true
	}
	for _, f := range c.filters {
		if !f.Allow(eventType) {
			return false
		}
	}
	return true
}

// EventTypeFilter filters by an event type whitelist.
type EventTypeFilter struct {
	allowed map[string]bool
}

// NewEventTypeFilter creates a whitelist filter from a comma-separated string.
// Returns nil for empty input (meaning no filtering).
func NewEventTypeFilter(commaSeparated string) *EventTypeFilter {
	if commaSeparated == "" {
		return nil
	}
	allowed := make(map[string]bool)
	for _, t := range strings.Split(commaSeparated, ",") {
		t = strings.TrimSpace(t)
		if t != "" {
			allowed[t] = true
		}
	}
	if len(allowed) == 0 {
		return nil
	}
	return &EventTypeFilter{allowed: allowed}
}

func (f *EventTypeFilter) Allow(eventType string) bool {
	return f.allowed[eventType]
}

// Types returns the whitelisted event types.
func (f *EventTypeFilter) Types() []string {
	types := make([]string, 0, len(f.allowed))
	for t := range f.allowed {
		types = append(types, t)
	}
	sort.Strings(types)
	return types
}

// RegexFilter filters event types by a regular expression.
type RegexFilter struct {
	re *regexp.Regexp
}

// NewRegexFilter compiles a regex and creates a filter. Returns nil, nil for empty input.
func NewRegexFilter(pattern string) (*RegexFilter, error) {
	if pattern == "" {
		return nil, nil
	}
	re, err := regexp.Compile(pattern)
	if err != nil {
		return nil, err
	}
	return &RegexFilter{re: re}, nil
}

func (f *RegexFilter) Allow(eventType string) bool {
	return f.re.MatchString(eventType)
}

func (f *RegexFilter) String() string {
	return f.re.String()
}
