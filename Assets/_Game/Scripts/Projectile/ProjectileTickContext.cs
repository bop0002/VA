public readonly struct ProjectileTickContext
{
    public readonly ITargetQuery EnemyTargets;
    public readonly ITargetQuery PlayerTargets;

    public ProjectileTickContext(ITargetQuery enemyTargets, ITargetQuery playerTargets)
    {
        EnemyTargets = enemyTargets;
        PlayerTargets = playerTargets;
    }

    // team = phe nguoi ban -> tra ve query cua phe DOI DIEN
    public ITargetQuery TargetsFor(Team team) => team == Team.Player ? EnemyTargets : PlayerTargets;
}
