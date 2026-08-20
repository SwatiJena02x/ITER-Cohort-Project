import litellm


# Disable LiteLLM cache
litellm.cache = None


original_completion = litellm.completion


def remove_cache_breakpoint(messages):

    if not messages:
        return messages

    for msg in messages:

        if isinstance(msg, dict):

            # Remove unsupported field
            msg.pop(
                "cache_breakpoint",
                None
            )

            # Check content blocks
            content = msg.get("content")

            if isinstance(content, list):

                for block in content:

                    if isinstance(block, dict):

                        block.pop(
                            "cache_breakpoint",
                            None
                        )

    return messages



def patched_completion(*args, **kwargs):

    if "messages" in kwargs:

        kwargs["messages"] = remove_cache_breakpoint(
            kwargs["messages"]
        )


    # Disable caching
    kwargs.pop(
        "cache",
        None
    )


    return original_completion(
        *args,
        **kwargs
    )



# Replace LiteLLM function
litellm.completion = patched_completion