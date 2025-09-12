const aqi = {
  convert_to_groups: (aqi_data) => {
    var levels = [];
    var pollutant_groups = [];
    if (aqi_data.length == 0) return { levels: [{ index: 1, description: "Good", color: "#026440" }], pollutant_groups: [] };

    // levels
    const levelMap = {};
    aqi_data.forEach((item) => {
      if (!levelMap[item.level]) {
        levelMap[item.level] = {
          index: item.level,
          description: item.description,
          color: item.color
        };
      }
    });
    const sortedLevels = Object.values(levelMap).sort((a, b) => a.index - b.index);
    levels = sortedLevels;

    // pollutant_groups
    const rangeMap = {};
    aqi_data.forEach((item) => {
      const key = item.pollutant + "|" + item.timestep;
      if (!rangeMap[key]) {
        rangeMap[key] = {
          pollutant_uri: item.pollutant_uri,
          pollutant: item.pollutant,
          timestep_uri: item.timestep_uri,
          timestep: item.timestep,
          ranges: []
        };
      }
      rangeMap[key].ranges.push({
        pollutant_uri: item.pollutant_uri,
        pollutant: item.pollutant,
        timestep_uri: item.timestep_uri,
        timestep: item.timestep,
        level: item.level,
        range_from: item.range_from !== undefined ? Number(item.range_from) : null,
        range_to: item.range_to !== undefined ? Number(item.range_to) : null
      });
    });
    // Sort ranges by level index for each pollutant/timestep
    Object.values(rangeMap).forEach((pr) => {
      pr.ranges.sort((a, b) => a.level - b.level);
    });
    pollutant_groups = Object.values(rangeMap);
    return { levels, pollutant_groups };
  },

  add_pollutant_group: (pollutant, timestep, levels) => {
    return {
      pollutant: pollutant.label,
      timestep: timestep.label,
      pollutant_uri: pollutant.value,
      timestep_uri: timestep.value,
      ranges: levels.map((level) => ({
        pollutant_uri: pollutant.value,
        pollutant: pollutant.label,
        timestep_uri: timestep.value,
        timestep: timestep.label,
        level: level.index,
        range_from: null,
        range_to: null
      }))
    };
  },

  add_range: (pollutant_groups, index) => {
    return {
      pollutant_uri: pollutant_groups.value,
      pollutant: pollutant_groups.label,
      timestep_uri: pollutant_groups.value,
      timestep: pollutant_groups.label,
      level: index,
      range_from: null,
      range_to: null
    };
  },

  flatten_pollutant_groups: (pollutant_groups, levels) => {
    return pollutant_groups
      .map((pg) => {
        return pg.ranges.map((r) => {
          const levelInfo = levels.find((lvl) => lvl.index === r.level) || {};
          return {
            pollutant_uri: pg.pollutant_uri,
            pollutant: pg.pollutant,
            timestep_uri: pg.timestep_uri,
            timestep: pg.timestep,
            level: r.level,
            range_from: r.range_from,
            range_to: r.range_to,
            color: levelInfo.color,
            description: levelInfo.description
          };
        });
      })
      .flat();
  }
};
export default aqi;
