#include <mlgame_client.hpp>

void ml_loop(json init_atgs);

int main()
{
    ml_loop(get_init_args());
    return 0;
}

/* Append user-defined ml_loop() from here. */
